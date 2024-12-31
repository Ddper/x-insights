from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict


class Base(BaseModel):
    id: Optional[UUID] = Field(None, description="Unique id")
    created_at: Optional[datetime] = Field(None, description="Creation datetime")
    updated_at: Optional[datetime] = Field(None, description="Update datetime")

    model_config = ConfigDict(from_attributes=True)
