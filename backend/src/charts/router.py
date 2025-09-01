from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional, Literal

from src.db.session import get_db
from src.auth.service import get_current_user
from src.auth.models import User
from src.charts.service import expenses_by_category, spend_trend

router = APIRouter(prefix="/charts", tags=["charts"])

@router.get("/expenses-by-category")
def chart_expenses_by_category(
    start: Optional[datetime] = Query(default=None),
    end: Optional[datetime] = Query(default=None),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return expenses_by_category(db, user, start, end)

@router.get("/spend-trend")
def chart_spend_trend(
    granularity: Literal["day","month"] = Query(default="month"),
    kind: Literal["expense","income"] = Query(default="expense"),
    start: Optional[datetime] = Query(default=None),
    end: Optional[datetime] = Query(default=None),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return spend_trend(db, user, granularity, start, end, kind)
