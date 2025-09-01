from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey, text
from src.db.base import Base
import uuid
from datetime import datetime

class Attachment(Base):
    __tablename__ = "attachments"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    transaction_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("transactions.id", ondelete="SET NULL"))
    file_name: Mapped[str]
    mime_type: Mapped[str]
    size_bytes: Mapped[int]
    storage_key: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(server_default=text("now()"))
