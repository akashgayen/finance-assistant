from __future__ import annotations
from datetime import datetime
from decimal import Decimal
from typing import Optional, Literal, List
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict
from pydantic import BaseModel, ConfigDict
from typing import List

TransactionType = Literal["income", "expense"]

class TransactionBase(BaseModel):
    type: TransactionType
    amount: Decimal = Field(gt=0)
    currency: str = Field(default="INR", min_length=3, max_length=3)
    category_id: Optional[UUID] = None
    merchant: Optional[str] = None
    notes: Optional[str] = None
    occurred_at: datetime

class TransactionCreate(TransactionBase):
    pass

class TransactionUpdate(BaseModel):
    type: Optional[TransactionType] = None
    amount: Optional[Decimal] = Field(default=None, gt=0)
    currency: Optional[str] = Field(default=None, min_length=3, max_length=3)
    category_id: Optional[UUID] = None
    merchant: Optional[str] = None
    notes: Optional[str] = None
    occurred_at: Optional[datetime] = None

class TransactionOut(TransactionBase):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    user_id: UUID
    created_at: datetime

class PageParams(BaseModel):
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)

class TransactionFilters(BaseModel):
    start: Optional[datetime] = None
    end: Optional[datetime] = None
    category_id: Optional[UUID] = None
    type: Optional[TransactionType] = None
    min_amount: Optional[Decimal] = None
    max_amount: Optional[Decimal] = None
    search: Optional[str] = Field(default=None, description="Matches merchant or notes")

class TransactionPage(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    items: List[TransactionOut]
    total: int
    page: int
    page_size: int