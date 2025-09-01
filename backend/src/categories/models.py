from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey, text
from src.db.base import Base
import uuid
from datetime import datetime

class Category(Base):
    __tablename__ = "categories"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    name: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(server_default=text("now()"))
