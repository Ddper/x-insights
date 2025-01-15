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
