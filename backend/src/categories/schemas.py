from __future__ import annotations
from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID
from datetime import datetime
from typing import Optional, List

class CategoryCreate(BaseModel):
    name: str = Field(min_length=1, max_length=50)

class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=50)

class CategoryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    user_id: UUID
    name: str
    created_at: datetime
