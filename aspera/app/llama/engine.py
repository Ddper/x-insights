from anyio.streams.memory import MemoryObjectSendStream, MemoryObjectReceiveStream

from phoenix.otel import register
from openinference.instrumentation.llama_index import LlamaIndexInstrumentor
from llama_index.core import Settings, VectorStoreIndex, SimpleDirectoryReader, StorageContext
from llama_index.core.callbacks import CallbackManager
from llama_index.core.agent import ReActAgent
from llama_index.core.tools import QueryEngineTool

from llama_index.llms.dashscope import DashScope
from llama_index.embeddings.dashscope import (DashScopeEmbedding, DashScopeTextEmbeddingModels,
                                              DashScopeTextEmbeddingType)

from llama_index.core.memory import ChatMemoryBuffer
from llama_index.core.storage.chat_store import SimpleChatStore

from app.settings import Settings as AppSettings

chat_store = SimpleChatStore()


async def init_llama_index_settings(settings: AppSettings):
    callback_manager = CallbackManager()
    Settings.callback_manager = callback_manager

    Settings.chunk_size = settings.chunk_size
    Settings.chunk_overlap = settings.chunk_overlap
    llm = DashScope(model_name=settings.dashscope_model_name, api_key=settings.dashscope_api_key, temperature=0)
    Settings.llm = llm

    embed_model = DashScopeEmbedding(
        model_name=DashScopeTextEmbeddingModels.TEXT_EMBEDDING_V3,
        text_type=DashScopeTextEmbeddingType.TEXT_TYPE_DOCUMENT,
        api_key=settings.dashscope_api_key,
        embed_batch_size=2
    )
    Settings.embed_model = embed_model

    # tracer_provider = register(
    #   endpoint=settings.tracer_provider_endpoint,
    # )
    #
    # LlamaIndexInstrumentor().instrument(tracer_provider=tracer_provider)
