# src/transactions/service.py
from datetime import datetime
from typing import Tuple, List
from uuid import UUID

from sqlalchemy import select, func, or_
from sqlalchemy.orm import Session

from src.transactions.models import Transaction
from src.transactions.schemas import (
    TransactionCreate, TransactionUpdate, TransactionOut,
    TransactionFilters, PageParams, TransactionPage,
)
from src.auth.models import User

def create_transaction(db: Session, user: User, payload: TransactionCreate) -> Transaction:
    tx = Transaction(
        user_id=user.id,
        type=payload.type,
        amount=float(payload.amount),  # stored as numeric in DB
        currency=payload.currency,
        category_id=payload.category_id,
        merchant=payload.merchant,
        notes=payload.notes,
        occurred_at=payload.occurred_at,
    )
    db.add(tx)
    db.commit()
    db.refresh(tx)
    return tx

def get_transaction(db: Session, user: User, tx_id: UUID) -> Transaction | None:
    stmt = select(Transaction).where(Transaction.id == tx_id, Transaction.user_id == user.id)
    return db.execute(stmt).scalars().first()

def update_transaction(db: Session, user: User, tx: Transaction, payload: TransactionUpdate) -> Transaction:
    for field, value in payload.model_dump(exclude_unset=True).items():
        if field == "amount" and value is not None:
            setattr(tx, field, float(value))
        else:
            setattr(tx, field, value)
    db.add(tx)
    db.commit()
    db.refresh(tx)
    return tx

def delete_transaction(db: Session, user: User, tx: Transaction) -> None:
    db.delete(tx)
    db.commit()

def list_transactions(
    db: Session,
    user: User,
    filters: TransactionFilters,
    page: PageParams,
) -> TransactionPage:
    stmt = select(Transaction).where(Transaction.user_id == user.id)

    if filters.start:
        stmt = stmt.where(Transaction.occurred_at >= filters.start)
    if filters.end:
        stmt = stmt.where(Transaction.occurred_at <= filters.end)
    if filters.category_id:
        stmt = stmt.where(Transaction.category_id == filters.category_id)
    if filters.type:
        stmt = stmt.where(Transaction.type == filters.type)
    if filters.min_amount is not None:
        stmt = stmt.where(Transaction.amount >= float(filters.min_amount))
    if filters.max_amount is not None:
        stmt = stmt.where(Transaction.amount <= float(filters.max_amount))
    if filters.search:
        ilike = f"%{filters.search}%"
        stmt = stmt.where(or_(Transaction.merchant.ilike(ilike), Transaction.notes.ilike(ilike)))

    # total count on the filtered statement
    total = db.scalar(select(func.count()).select_from(stmt.subquery())) or 0

    # page-based pagination -> LIMIT/OFFSET
    offset = (page.page - 1) * page.page_size
    items_orm = (
        db.execute(
            stmt.order_by(Transaction.occurred_at.desc())
               .offset(offset)
               .limit(page.page_size)
        ).scalars().all()
    )
    
    items = [TransactionOut.model_validate(x, from_attributes=True) for x in items_orm]

    return TransactionPage(
        items=items,
        total=total,
        page=page.page,
        page_size=page.page_size,
    )
