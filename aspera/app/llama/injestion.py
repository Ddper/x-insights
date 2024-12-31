from llama_index.core import StorageContext, VectorStoreIndex
from llama_index.readers.web import TrafilaturaWebReader

from llama_index.vector_stores.postgres import PGVectorStore

from app.settings import get_settings


settings = get_settings()


async def ingest_web(url: str) -> None:
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
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    documents = await TrafilaturaWebReader().aload_data(urls=[url])
    # node_parser = SentenceSplitter(chunk_size=Settings.chunk_size, chunk_overlap=Settings.chunk_overlap)
    # nodes = await node_parser.aget_nodes_from_documents(documents)
    # VectorStoreIndex(
    #     nodes=nodes,
    #     storage_context=storage_context,
    #     embed_model=Settings.embed_model,
    #     show_progress=True
    # )
    index = VectorStoreIndex.from_documents(documents=documents, storage_context=storage_context, show_progress=True)
    # query_engine = index.as_query_engine()
    # print(query_engine.query("What are agents?"))
