import re

from markitdown import MarkItDown
from llama_index.core.node_parser.file.markdown import TextNode
from llama_index.core import StorageContext, VectorStoreIndex, SummaryIndex, Settings
# from llama_index.core.text_splitter import SentenceSplitter
from llama_index.core.node_parser import (SentenceWindowNodeParser, SemanticSplitterNodeParser, SentenceSplitter,
                                          MarkdownNodeParser, MarkdownElementNodeParser)
from llama_index.storage.index_store.postgres import PostgresIndexStore
from llama_index.storage.docstore.postgres import PostgresDocumentStore
from llama_index.readers.web import TrafilaturaWebReader

from llama_index.vector_stores.postgres import PGVectorStore

from app.settings import get_settings
from app.utils.document import hash_url


settings = get_settings()


async def build_storage_context() -> StorageContext:
    vector_store = PGVectorStore.from_params(
        connection_string=settings.vector_database_url,
        async_connection_string=settings.async_vector_database_url,
        table_name=settings.vector_table_name,
        schema_name=settings.vector_schema_name,
        embed_dim=1024,
        hnsw_kwargs={
            "hnsw_m": 16,
            "hnsw_ef_construction": 64,
            "hnsw_ef_search": 40,
            "hnsw_dist_method": "vector_cosine_ops",
        },
        # create_engine_kwargs=database_url.query
    )
    index_store = PostgresIndexStore.from_uri(
        uri=settings.vector_database_url,
        schema_name=settings.vector_schema_name
    )
    doc_store = PostgresDocumentStore.from_uri(
        uri=settings.vector_database_url,
        schema_name=settings.vector_schema_name
    )
    storage_context = StorageContext.from_defaults(
        vector_store=vector_store,
        index_store=index_store,
        docstore=doc_store
    )
    return storage_context


def split_text_into_sentences(text):
    sentence_endings = re.compile(r'(?<=[。！？.!?])')
    sentences = sentence_endings.split(text)
    return [s.strip() for s in sentences if s.strip()]


async def ingest_web(url: str) -> None:
    storage_context = await build_storage_context()
    hash_id = hash_url(url)
    documents = await TrafilaturaWebReader().aload_data(urls=[url])
    for document in documents:
        document.metadata = {"hash_id": hash_id}

    # node_parser = SemanticSplitterNodeParser(embed_model=Settings.embed_model)
    sentence_splitter = SentenceSplitter()
    node_parser = SentenceWindowNodeParser.from_defaults(
        window_size=3,
        window_metadata_key="window",
        original_text_metadata_key="original_text",
    )
    Settings.text_splitter = sentence_splitter
    nodes = await node_parser.aget_nodes_from_documents(documents)

    # md = MarkItDown()
    # md_document = md.convert_url(url=url)
    # node = TextNode(text=md_document.text_content)
    # node_parser = MarkdownElementNodeParser()
    # nodes = await node_parser.aget_nodes_from_node(node)

    index = VectorStoreIndex(
        nodes=nodes,
        storage_context=storage_context,
        embed_model=Settings.embed_model,
        show_progress=True
    )
    index.set_index_id(hash_id)

    summary_node_parser = SentenceSplitter(chunk_size=Settings.chunk_size, chunk_overlap=Settings.chunk_overlap)
    summary_nodes = await summary_node_parser.aget_nodes_from_documents(documents)
    summary_index = SummaryIndex(nodes=summary_nodes, storage_context=storage_context, show_progress=True)
    summary_index.set_index_id(f"summary_{hash_id}")
