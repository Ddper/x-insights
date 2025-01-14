import asyncio

from markitdown import MarkItDown
from llama_index.core.node_parser.file.markdown import TextNode
from llama_index.core.node_parser import MarkdownNodeParser, MarkdownElementNodeParser
from llama_index.core import VectorStoreIndex

from app.settings import get_settings
from app.llama.engine import init_llama_index_settings
from app.llama.engine import build_storage_context

settings = get_settings()


def main():
    asyncio.run(ingest_md())


async def ingest_md():
    await init_llama_index_settings(settings)
    storage_context = await build_storage_context()

    # md = MarkItDown()
    # md_document = md.convert_url("https://docs.llamaindex.ai/en/stable/#introduction")
    # text_node = TextNode(text=md_document.text_content)
    markdown_text = """
    # Title
    This is a paragraph.
    ## Subtitle
    - List item 1
    - List item 2
    """
    text_node = TextNode(text=markdown_text)
    node_parser = MarkdownElementNodeParser()

    nodes = await node_parser.aget_nodes_from_node(text_node)

    for node in nodes:
        print(f"Header: {node.metadata.get('header_path', 'No Header')}")
        print(f"Content: {node.text}\n")

    index = VectorStoreIndex(nodes=nodes, storage_context=storage_context)


if __name__ == "__main__":
    main()
