from sqlalchemy import select, func
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Literal, Optional

from src.transactions.models import Transaction
from src.categories.models import Category
from src.auth.models import User

Granularity = Literal["day", "month"]

def expenses_by_category(
    db: Session,
    user: User,
    start: Optional[datetime] = None,
    end: Optional[datetime] = None,
):
    # LEFT JOIN to include uncategorized
    stmt = (
        select(
            func.coalesce(Category.name, "Uncategorized").label("label"),
            func.sum(Transaction.amount).label("value"),
        )
        .select_from(Transaction)
        .join(Category, Category.id == Transaction.category_id, isouter=True)
        .where(Transaction.user_id == user.id)
        .where(Transaction.type == "expense")
    )
    if start:
        stmt = stmt.where(Transaction.occurred_at >= start)
    if end:
        stmt = stmt.where(Transaction.occurred_at <= end)

    stmt = stmt.group_by("label").order_by(func.sum(Transaction.amount).desc())
    rows = db.execute(stmt).all()
    labels = [r.label for r in rows]
    data = [float(r.value or 0) for r in rows]
    return {"labels": labels, "datasets": [{"label": "Expenses by Category", "data": data}]}

def spend_trend(
    db: Session,
    user: User,
    granularity: Granularity = "month",
    start: Optional[datetime] = None,
    end: Optional[datetime] = None,
    kind: Literal["expense", "income"] = "expense",
):
    dt = func.date_trunc(granularity, Transaction.occurred_at).label("period")
    stmt = (
        select(
            dt,
            func.sum(Transaction.amount).label("value"),
        )
        .where(Transaction.user_id == user.id)
        .where(Transaction.type == kind)
    )
    if start:
        stmt = stmt.where(Transaction.occurred_at >= start)
    if end:
        stmt = stmt.where(Transaction.occurred_at <= end)

    stmt = stmt.group_by(dt).order_by(dt.asc())
    rows = db.execute(stmt).all()
    labels = [r.period.isoformat() for r in rows]
    data = [float(r.value or 0) for r in rows]
    title = f"{kind.title()} Trend ({granularity})"
    return {"labels": labels, "datasets": [{"label": title, "data": data}]}
