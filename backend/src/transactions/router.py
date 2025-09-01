from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from datetime import datetime

from src.db.session import get_db
from src.auth.service import get_current_user
from src.auth.models import User
from src.transactions.schemas import (
    TransactionCreate, TransactionUpdate, TransactionOut,
    TransactionFilters, PageParams, TransactionPage,
)
from src.transactions.service import (
    create_transaction, get_transaction, update_transaction,
    delete_transaction, list_transactions,
)

router = APIRouter(prefix="/transactions", tags=["transactions"])

@router.post("", response_model=TransactionOut, status_code=status.HTTP_201_CREATED)
def create_tx(
    payload: TransactionCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    tx = create_transaction(db, user, payload)
    return TransactionOut.model_validate(tx, from_attributes=True)

@router.get("", response_model=TransactionPage)
def list_tx(
    start: Optional[datetime] = Query(default=None),
    end: Optional[datetime] = Query(default=None),
    category_id: Optional[UUID] = Query(default=None),
    type: Optional[str] = Query(default=None, pattern="^(income|expense)$"),
    min_amount: Optional[float] = Query(default=None, ge=0),
    max_amount: Optional[float] = Query(default=None, ge=0),
    search: Optional[str] = Query(default=None, min_length=1, max_length=100),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    filters = TransactionFilters(
        start=start, end=end,
        category_id=category_id,
        type=type,
        min_amount=min_amount, max_amount=max_amount,
        search=search,
    )
    params = PageParams(page=page, page_size=page_size)
    result = list_transactions(db, user, filters, params)  # likely returns a Page-like object

    # Ensure items are Pydantic DTOs, not ORM models
    items = [TransactionOut.model_validate(x, from_attributes=True) for x in result.items]
    return TransactionPage(
        items=items,
        total=result.total,
        page=result.page,
        page_size=result.page_size,
    )

@router.get("/{tx_id}", response_model=TransactionOut)
def get_tx(
    tx_id: UUID,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    tx = get_transaction(db, user, tx_id)
    if not tx:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")
    return TransactionOut.model_validate(tx, from_attributes=True)

@router.patch("/{tx_id}", response_model=TransactionOut)
def patch_tx(
    tx_id: UUID,
    payload: TransactionUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    tx = get_transaction(db, user, tx_id)
    if not tx:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")
    tx = update_transaction(db, user, tx, payload)
    return TransactionOut.model_validate(tx, from_attributes=True)

@router.delete("/{tx_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_tx(
    tx_id: UUID,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    tx = get_transaction(db, user, tx_id)
    if not tx:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")
    delete_transaction(db, user, tx)
    return None
