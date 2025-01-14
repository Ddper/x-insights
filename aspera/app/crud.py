import json
from typing import Optional, List, Sequence

from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, update
from sqlalchemy.dialects.postgresql import UUID

from app.schemas.document import DocumentSchema, CreateDocumentSchema
from app.models.document import Document, DocumentIndexStatusEnum
from app.utils.document import hash_url


async def list_documents(
        db: AsyncSession,
        limit: Optional[int] = 10
) -> Optional[List[DocumentSchema]]:
    stmt = select(Document)
    stmt = stmt.limit(limit)
    result = await db.execute(stmt)
    documents = result.scalars().all()
    return [DocumentSchema.from_orm(doc) for doc in documents]


async def fetch_document(db: AsyncSession, document_id: str) -> Optional[DocumentSchema]:
    stmt = select(Document).where(Document.id == document_id)
    result = await db.execute(stmt)
    document = result.scalars().first()
    if document is not None:
        return DocumentSchema.from_orm(document)
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
    return DocumentSchema.from_orm(document)


async def update_document_status(db: AsyncSession, document_id: UUID, status: DocumentIndexStatusEnum):
    stmt = update(Document).where(Document.id == document_id)
    stmt = stmt.values(status=status)
    await db.execute(stmt)
    await db.commit()
