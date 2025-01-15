import json
from typing import Optional, List, Sequence

from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, update
from sqlalchemy.dialects.postgresql import UUID

from app.schemas.document import DocumentSchema, CreateDocumentSchema
from app.schemas.chat import CreateChatSchema, ChatSchema
from app.models.document import Document, DocumentIndexStatusEnum
from app.models.chat import Chat, ChatDocument
from app.utils.document import hash_url
from app.llama.engine import build_chat_memory
from app.settings import get_settings


settings = get_settings()


async def list_documents(
        db: AsyncSession,
        limit: Optional[int] = 10
) -> Optional[List[DocumentSchema]]:
    stmt = select(Document)
    stmt = stmt.limit(limit)
    result = await db.execute(stmt)
    documents = result.scalars().all()
    return [DocumentSchema.model_validate(doc) for doc in documents]


async def fetch_document(db: AsyncSession, document_id: str) -> Optional[DocumentSchema]:
    stmt = select(Document).where(Document.id == document_id)
    result = await db.execute(stmt)
    document = result.scalars().first()
    if document is not None:
        return DocumentSchema.model_validate(document)
    return None


async def create_document(
        db: AsyncSession,
        payload: CreateDocumentSchema
) -> DocumentSchema:
    document = Document()
    document.url = payload.url
    document.hash_id = hash_url(payload.url)
    document.metadata_map = {}
    document.description = payload.description
    db.add(document)
    await db.commit()
    await db.refresh(document)
    return DocumentSchema.model_validate(document)


async def update_document_status(db: AsyncSession, document_id: UUID, status: DocumentIndexStatusEnum):
    stmt = update(Document).where(Document.id == document_id)
    stmt = stmt.values(status=status)
    await db.execute(stmt)
    await db.commit()


async def fetch_chat(
        db: AsyncSession, chat_id: str
) -> Optional[ChatSchema]:
    stmt = (select(Chat)
            .options(
                joinedload(Chat.chat_documents).subqueryload(ChatDocument.document)
            )
            .where(Chat.id == chat_id))
    result = await db.execute(stmt)
    chat = result.scalars().first()
    if chat is not None:
        chat_memory = build_chat_memory(settings, chat_id)
        chat_dict = {
            **chat.__dict__,
            "documents": [
                chat_doc.document for chat_doc in chat.chat_documents
            ],
            "chat_history": chat_memory.get_all()
        }
        return ChatSchema(**chat_dict)
    return None


async def create_chat(
        db: AsyncSession,
        chat_payload: CreateChatSchema
) -> ChatSchema:
    chat = Chat()
    chat_documents = [ChatDocument(document_id=document_id, chat=chat) for document_id in chat_payload.document_ids]
    db.add(chat)
    db.add_all(chat_documents)
    await db.commit()
    await db.refresh(chat)
    return await fetch_chat(db, chat.id)
