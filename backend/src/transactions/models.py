from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey, text, CheckConstraint
from src.db.base import Base
import uuid
from datetime import datetime

class Transaction(Base):
    __tablename__ = "transactions"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    type: Mapped[str] = mapped_column()  # 'income' or 'expense'
    amount: Mapped[float] = mapped_column()
    currency: Mapped[str] = mapped_column(default="INR")
    category_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("categories.id"), nullable=True)
    merchant: Mapped[str | None]
    notes: Mapped[str | None]
    occurred_at: Mapped[datetime]
    created_at: Mapped[datetime] = mapped_column(server_default=text("now()"))

    __table_args__ = (
        CheckConstraint("type in ('income','expense')"),
        CheckConstraint("amount >= 0"),
    )
