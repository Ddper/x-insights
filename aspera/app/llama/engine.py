from typing import List
from anyio.streams.memory import MemoryObjectSendStream, MemoryObjectReceiveStream

from phoenix.otel import register
from openinference.instrumentation.llama_index import LlamaIndexInstrumentor
from llama_index.core import (Settings, VectorStoreIndex, SimpleDirectoryReader, StorageContext,
                              get_response_synthesizer, SummaryIndex, load_index_from_storage)
from llama_index.core.vector_stores.types import MetadataFilters, ExactMatchFilter
from llama_index.core.base.base_query_engine import BaseQueryEngine
from llama_index.core.query_engine import RetrieverQueryEngine, SubQuestionQueryEngine
from llama_index.core.postprocessor import SimilarityPostprocessor, MetadataReplacementPostProcessor
from llama_index.core.response_synthesizers.type import ResponseMode
from llama_index.core.callbacks import CallbackManager
from llama_index.core.agent import ReActAgent
from llama_index.core.tools import QueryEngineTool

from llama_index.llms.openai_like import OpenAILike
from llama_index.llms.openai import OpenAI
from llama_index.llms.dashscope import DashScope
from llama_index.embeddings.dashscope import (DashScopeEmbedding, DashScopeTextEmbeddingModels,
                                              DashScopeTextEmbeddingType)
from llama_index.agent.openai import OpenAIAgent

from llama_index.core.memory import ChatMemoryBuffer
from llama_index.core.storage.chat_store import SimpleChatStore
from llama_index.vector_stores.postgres import PGVectorStore
from llama_index.storage.index_store.postgres import PostgresIndexStore
from llama_index.storage.chat_store.postgres import PostgresChatStore
from llama_index.core.indices.base import BaseIndex

from app.settings import Settings as AppSettings
from app.schemas.document import DocumentSchema
from app.llama.callback_handlers import ChatCallbackHandler
from app.llama.injestion import build_storage_context
from app.settings import get_settings


def build_chat_memory(settings: AppSettings, chat_id: str) -> ChatMemoryBuffer:
    # chat_store = SimpleChatStore()
    chat_store = PostgresChatStore.from_uri(
        uri=settings.async_database_url,
        schema_name=settings.chat_schema_name,
        table_name=settings.chat_table_name
    )
    chat_memory = ChatMemoryBuffer.from_defaults(
        token_limit=3000,
        chat_store=chat_store,
        chat_store_key=chat_id
    )
    return chat_memory


async def init_llama_index_settings(settings: AppSettings):
    callback_manager = CallbackManager()
    Settings.callback_manager = callback_manager

    Settings.chunk_size = settings.chunk_size
    Settings.chunk_overlap = settings.chunk_overlap
    llm = DashScope(model_name=settings.dashscope_model_name, api_key=settings.dashscope_api_key, temperature=1)
    # llm = OpenAILike(model="deepseek-chat", api_base="https://api.deepseek.com/beta", api_key="")
    Settings.llm = llm

    embed_model = DashScopeEmbedding(
        model_name=DashScopeTextEmbeddingModels.TEXT_EMBEDDING_V3,
        text_type=DashScopeTextEmbeddingType.TEXT_TYPE_DOCUMENT,
        api_key=settings.dashscope_api_key,
        embed_batch_size=2
    )
    Settings.embed_model = embed_model

    tracer_provider = register(
      endpoint=settings.tracer_provider_endpoint,
    )

    LlamaIndexInstrumentor().instrument(tracer_provider=tracer_provider)


def index_to_query_engine(document_hash_id: str, index: BaseIndex) -> BaseQueryEngine:
    filters = MetadataFilters(filters=[ExactMatchFilter(key="hash_id", value=document_hash_id)])
    # return index.as_query_engine(**{"similarity_top_k": 3, "filters": filters})

    retriever = index.as_retriever(
        similarity_top_k=10,
        filters=filters,
    )
    streaming_response_synthesizer = get_response_synthesizer(
        streaming=False,
        verbose=True,
        response_mode=ResponseMode.COMPACT
    )
    streaming_query_engine = RetrieverQueryEngine(
        retriever=retriever,
        response_synthesizer=streaming_response_synthesizer,
        node_postprocessors=[SimilarityPostprocessor(similarity_cutoff=0.1),
                             MetadataReplacementPostProcessor(target_metadata_key="window")],
    )
    return streaming_query_engine


async def get_agent_engine(
        chat_id: str,
        settings: AppSettings,
        send_stream: MemoryObjectSendStream,
        documents: List[DocumentSchema]
) -> ReActAgent | OpenAIAgent:
    storage_context = await build_storage_context()
    tools = []
    for document in documents:
        index = load_index_from_storage(storage_context=storage_context, index_id=document.hash_id)
        tools.append(QueryEngineTool.from_defaults(
            query_engine=index_to_query_engine(document.hash_id, index),
            name=document.description.replace(" ", "-"),
            description=document.description
        ))
        summary_index = load_index_from_storage(storage_context=storage_context, index_id=f"summary_{document.hash_id}")
        tools.append(QueryEngineTool.from_defaults(
            query_engine=summary_index.as_query_engine(),
            name="summary-" + document.description.replace(" ", "-"),
            description=document.description
        ))

    callback_handler = ChatCallbackHandler(send_stream)
    callback_manager = CallbackManager([callback_handler])
    chat_memory = build_chat_memory(settings, chat_id=chat_id)
    # return OpenAIAgent.from_tools(
    #     tools=tools,
    #     llm=Settings.llm,
    #     memory=chat_memory,
    #     callback_manager=callback_manager
    # )
    return ReActAgent.from_tools(
        tools,
        callback_manager=callback_manager,
        memory=chat_memory,
        verbose=True
    )
