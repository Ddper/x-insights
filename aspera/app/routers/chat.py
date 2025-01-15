import json
from uuid import UUID
from typing import List

import anyio
from fastapi import APIRouter, Depends
from sse_starlette.sse import EventSourceResponse
from anyio.streams.memory import MemoryObjectReceiveStream, MemoryObjectSendStream
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud
from app.settings import get_settings
from app.llama.engine import get_agent_engine
from app.schemas.document import DocumentSchema
from app.schemas.chat import CreateChatSchema, ChatSchema, StreamedMessage
from app.models.document import DocumentIndexStatusEnum
from app.dependencies import get_db


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
    content = ""
    async with send_stream:
        async for text in streaming_response.async_response_gen():
            content += text
            await send_stream.send(StreamedMessage(content=content))


@router.get("/{chat_id}/message")
async def chat(
        chat_id: UUID,
        user_message: str,
        db: AsyncSession = Depends(get_db)
) -> EventSourceResponse:
    send_stream: MemoryObjectSendStream
    receive_stream: MemoryObjectReceiveStream
    send_stream, receive_stream = anyio.create_memory_object_stream(10)
    chat_schema = await crud.fetch_chat(db, str(chat_id))
    async def event_publisher():
        async with anyio.create_task_group() as tg:
            tg.start_soon(handle_agent_message, str(chat_id), user_message, send_stream, chat_schema.documents)

            async with receive_stream:
                async for message_obj in receive_stream:  # type: ignore
                    if isinstance(message_obj, StreamedMessage):
                        yield json.dumps({"content": message_obj.content})

    return EventSourceResponse(event_publisher())


@router.get("/{chat_id}")
async def get_chat(
        chat_id: str,
        db: AsyncSession = Depends(get_db)
) -> ChatSchema:
    return await crud.fetch_chat(db, chat_id)


@router.post("/")
async def create_chat(
        payload: CreateChatSchema,
        db: AsyncSession = Depends(get_db)
) -> ChatSchema:
    return await crud.create_chat(db, payload)
