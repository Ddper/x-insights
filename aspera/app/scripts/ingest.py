import asyncio

from app.settings import get_settings
from app.llama.injestion import ingest_web
from app.llama.engine import init_llama_index_settings

settings = get_settings()


async def ingest():
    await init_llama_index_settings(settings)
    await ingest_web("https://docs.llamaindex.ai/en/stable/#introduction")


def main():
    asyncio.run(ingest())


if __name__ == "__main__":
    main()
