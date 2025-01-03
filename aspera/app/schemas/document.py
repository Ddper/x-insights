from typing import Optional, Dict, Any, Annotated

from pydantic import BaseModel, AfterValidator


from app.db import SessionLocal
from app.schemas.base import Base
from app.utils.document import hash_url
from app.models import document as document_model


class DocumentSchema(Base):
    hash_id: str
    url: str
    metadata_map: Optional[Dict[str, Any]]
    status: document_model.DocumentIndexStatusEnum


def url_must_be_unique(v: Any):
    with SessionLocal() as db:
        if db.query(document_model.Document).filter_by(hash_id=hash_url(v)).first():
            raise ValueError("This url already exist")
    return v


class CreateDocumentSchema(BaseModel):
    url: Annotated[str, AfterValidator(url_must_be_unique)]
    description: str
