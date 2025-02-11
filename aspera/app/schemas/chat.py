from typing import List
from uuid import UUID

from typing import Optional
from pydantic import BaseModel

from llama_index.core.base.llms.types import ChatMessage

from app.schemas.base import Base
from app.schemas.document import DocumentSchema


class ChatSchema(Base):

    title: Optional[str]
    documents: List[DocumentSchema]
    chat_history: List[ChatMessage]


class CreateChatSchema(BaseModel):

    document_ids: List[UUID]


class StreamedMessage(BaseModel):

    content: str


class StreamedEvent(BaseModel):

    content: str


class ClientAttachment(BaseModel):
    name: str
    contentType: str
    url: str


class ToolInvocation(BaseModel):
    toolCallId: str
    toolName: str
    args: dict
    result: dict


class ClientMessage(BaseModel):
    role: str
    content: str
    experimental_attachments: Optional[List[ClientAttachment]] = None
    toolInvocations: Optional[List[ToolInvocation]] = None


class ChatRequest(BaseModel):
    id: UUID
    messages: List[ClientMessage]
    modelId: str
