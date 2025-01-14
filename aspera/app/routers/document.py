from typing import List, Optional, Annotated

from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import UUID

from app.dependencies import get_db
from app.schemas.document import DocumentSchema, CreateDocumentSchema
from app.models.document import Document, DocumentIndexStatusEnum
from app.llama.engine import init_llama_index_settings
from app.llama.injestion import ingest_web
from app import crud
from app.settings import get_settings
from app.db import AsyncSessionLocal

settings = get_settings()

router = APIRouter(
    prefix="/documents",
    tags=["documents"]
)


@router.get("/")
async def list_documents(
        db: AsyncSession = Depends(get_db)
) -> List[DocumentSchema]:
    documents = await crud.list_documents(db)
    return documents


async def ingest(document_id: UUID, url: str):
    await init_llama_index_settings(settings)
    await ingest_web(url)
    async with AsyncSessionLocal() as db:
        await crud.update_document_status(db, document_id, DocumentIndexStatusEnum.SUCCESS)


@router.post("/")
async def create_document(
        payload: CreateDocumentSchema,
        db: AsyncSession = Depends(get_db),
        background_tasks: BackgroundTasks = None
) -> DocumentSchema:
    document = await crud.create_document(db, payload)
    background_tasks.add_task(ingest, document.id, payload.url)
    return document
