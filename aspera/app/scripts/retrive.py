import asyncio

from llama_index.core import VectorStoreIndex
from llama_index.vector_stores.postgres import PGVectorStore
from llama_index.core.vector_stores.types import (
    MetadataFilter,
    MetadataFilters,
)
from app.settings import get_settings
from app.llama.engine import init_llama_index_settings


async def retrieve():
    settings = get_settings()
    await init_llama_index_settings(settings)

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

    index = VectorStoreIndex.from_vector_store(vector_store=vector_store)

    filters = MetadataFilters(
        filters=[
            MetadataFilter(key="hash_id", value="b455685c3a78d70cbfc46e4d6e84c0d7")
        ],
        condition="and",
    )

    retriever = index.as_retriever(
        similarity_top_k=10,
        filters=filters,
    )

    retrieved_nodes = retriever.retrieve("Who is LlamaIndex for?")

    for node in retrieved_nodes:
        print(node.node.metadata)


if __name__ == "__main__":
    asyncio.run(retrieve())
