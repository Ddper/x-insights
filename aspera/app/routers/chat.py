import asyncio
import json
import time

import anyio

from uuid import UUID
from typing import List

from pydantic import BaseModel
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sse_starlette.sse import EventSourceResponse
from anyio.streams.memory import MemoryObjectReceiveStream, MemoryObjectSendStream
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud
from app.settings import get_settings
from app.llama.engine import get_agent_engine
from app.schemas.document import DocumentSchema
from app.schemas.chat import CreateChatSchema, ChatSchema, StreamedMessage, ChatRequest
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
    async with send_stream:
        async for text in streaming_response.async_response_gen():
            await send_stream.send(StreamedMessage(content=text))


async def stream_text(
        chat_id: UUID,
        user_message: str,
        chat_schema: ChatSchema,
        send_stream: MemoryObjectSendStream,
        receive_stream: MemoryObjectReceiveStream
):
    async with anyio.create_task_group() as tg:
        tg.start_soon(handle_agent_message, str(chat_id), user_message, send_stream, chat_schema.documents)

        async with receive_stream:
            async for message_obj in receive_stream:  # type: ignore
                if isinstance(message_obj, StreamedMessage):
                    yield "0:{text}\n".format(text=json.dumps(message_obj.content))
                    # yield json.dumps({"content": message_obj.content}
            yield "d:{text}\n".format(text=json.dumps({"finishReason": "stop"}))

@router.post("/{chat_id}/message")
async def chat(
        chat_id: UUID,
        request: ChatRequest,
        db: AsyncSession = Depends(get_db)
) -> StreamingResponse:
    messages = request.messages
    user_message = messages[-1].content
    send_stream: MemoryObjectSendStream
    receive_stream: MemoryObjectReceiveStream
    chat_schema = await crud.fetch_chat(db, str(chat_id))
    send_stream, receive_stream = anyio.create_memory_object_stream(10)
    response = StreamingResponse(stream_text(chat_id, user_message, chat_schema, send_stream, receive_stream),
                                 media_type="text/event-stream")
    response.headers["x-vercel-ai-data-stream"] = "v1"
    return response

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


async def fake_video_streamer():
    for i in range(10):
        yield f"{i} some fake video bytes\n"
        await asyncio.sleep(1)


@router.get("/fake-chat/")
async def fake_chat() -> StreamingResponse:
    return StreamingResponse(fake_video_streamer(), media_type="text/event-stream")
