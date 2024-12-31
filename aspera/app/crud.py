import json
from typing import Optional, List, Sequence

from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, update
from sqlalchemy.dialects.postgresql import UUID

from app.schemas import document as document_schema
from app.models import document as document_model
from app.utils.document import hash_url


async def list_documents(
        db: AsyncSession,
        limit: Optional[int] = 10
) -> Optional[List[document_schema.DocumentSchema]]:
    stmt = select(document_model.Document)
    stmt = stmt.limit(limit)
    result = await db.execute(stmt)
    documents = result.scalars().all()
    return [document_schema.DocumentSchema.from_orm(doc) for doc in documents]


async def fetch_document(db: AsyncSession, document_id: str) -> Optional[document_schema.DocumentSchema]:
    stmt = select(document_model.Document).where(document_model.Document.id == document_id)
    result = await db.execute(stmt)
    document = result.scalars().first()
    if document is not None:
        return document_schema.DocumentSchema.from_orm(document)
    return None


async def create_document(
        db: AsyncSession,
        payload: document_schema.CreateDocumentSchema
) -> document_schema.DocumentSchema:
    document = document_model.Document()
    document.url = payload.url
    document.hash_id = hash_url(payload.url)
    document.metadata_map = {}
    db.add(document)
    await db.commit()
    await db.refresh(document)
    return document_schema.DocumentSchema.from_orm(document)


async def update_document_status(db: AsyncSession, document_id: UUID, status: document_model.DocumentIndexStatusEnum):
    stmt = update(document_model.Document).where(document_model.Document.id == document_id)
    stmt = stmt.values(status=status)
    await db.execute(stmt)
    await db.commit()
