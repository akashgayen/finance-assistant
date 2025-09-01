# src/imports/models.py
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey, text, CheckConstraint
from src.db.base import Base
import uuid
from datetime import datetime

class ImportJob(Base):
    __tablename__ = "import_jobs"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    source: Mapped[str]  # e.g., 'receipt', 'pdf'
    status: Mapped[str]
    total_rows: Mapped[int | None]
    inserted_rows: Mapped[int | None]
    failed_rows: Mapped[int | None]
    error_message: Mapped[str | None]
    created_at: Mapped[datetime] = mapped_column(server_default=text("now()"))
    __table_args__ = (
        CheckConstraint("status in ('pending','processing','completed','failed')"),
    )
