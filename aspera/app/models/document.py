from enum import Enum

from sqlalchemy import Column, String, ForeignKey, VARCHAR
from sqlalchemy.dialects.postgresql import UUID, ENUM, JSONB
from sqlalchemy.orm import relationship

from app.models.base import Base


def to_pg_enum(enum_class) -> ENUM:
    return ENUM(enum_class, name=enum_class.__name__)


class DocumentIndexStatusEnum(str, Enum):
    INDEXING = "INDEXING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"


class Document(Base):
    hash_id = Column(VARCHAR(32), nullable=False, unique=True, index=True)
    url = Column(String, nullable=False)
    metadata_map = Column(JSONB, nullable=True)
    description = Column(String, nullable=True)
    status = Column(to_pg_enum(DocumentIndexStatusEnum), default=DocumentIndexStatusEnum.INDEXING)
