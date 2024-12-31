from typing import List, Optional, Annotated

from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import UUID

from app.dependencies import get_db
from app.schemas import document as document_schema
from app.models import document as document_model
from app.llama.engine import init_llama_index_settings
from app.llama.injestion import ingest_web
from app import crud
from app.settings import get_settings

settings = get_settings()

router = APIRouter(
    prefix="/documents",
    tags=["documents"]
)


@router.get("/")
async def list_documents(
        db: AsyncSession = Depends(get_db)
) -> List[document_schema.DocumentSchema]:
    documents = await crud.list_documents(db)
    return documents


async def ingest(document_id: UUID, url: str, db: AsyncSession):
    await init_llama_index_settings(settings)
    await ingest_web(url)
    await crud.update_document_status(db, document_id, document_model.DocumentIndexStatusEnum.SUCCESS)


@router.post("/")
async def create_document(
        payload: document_schema.CreateDocumentSchema,
        db: AsyncSession = Depends(get_db),
        background_tasks: BackgroundTasks = None
) -> document_schema.DocumentSchema:
    document = await crud.create_document(db, payload)
    background_tasks.add_task(ingest, document.id, payload.url, db)
    return document
