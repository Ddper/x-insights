import json
from uuid import UUID
from typing import List

import anyio
from fastapi import APIRouter
from sse_starlette.sse import EventSourceResponse
from anyio.streams.memory import MemoryObjectReceiveStream, MemoryObjectSendStream

from app.settings import get_settings
from app.llama.engine import get_agent_engine
from app.schemas.document import DocumentSchema
from app.models.document import DocumentIndexStatusEnum

settings = get_settings()

router = APIRouter(
    prefix="/chat",
    tags=["chat"]
)


async def handle_agent_message(
        chat_id: str,
        user_message: str,
        send_stream: MemoryObjectSendStream,
        documents: List[DocumentSchema]
):
    agent = await get_agent_engine(chat_id, settings, send_stream, documents)
    streaming_response = await agent.astream_chat(message=user_message)
    response = ""
    async with send_stream:
        async for text in streaming_response.async_response_gen():
            response += text
            await send_stream.send(response)


@router.get("/{chat_id}")
async def chat(
        chat_id: UUID,
        user_message: str
) -> EventSourceResponse:
    send_stream: MemoryObjectSendStream
    receive_stream: MemoryObjectReceiveStream
    send_stream, receive_stream = anyio.create_memory_object_stream(10)

    documents = [DocumentSchema(
        hash_id="9e95d8c76724cce008ddaae4663b3d90",
        url="https://docs.llamaindex.ai/en/stable/#introduction",
        description="The introduction of llamaindex",
        metadata_map={},
        status=DocumentIndexStatusEnum.SUCCESS
    )]

    async def event_publisher():
        async with anyio.create_task_group() as tg:
            tg.start_soon(handle_agent_message, str(chat_id), user_message, send_stream, documents)

            async with receive_stream:
                async for assistant_message in receive_stream:  # type: ignore
                    yield json.dumps({"content": str(assistant_message)})

    return EventSourceResponse(event_publisher())
