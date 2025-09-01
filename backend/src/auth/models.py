from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import text
from src.db.base import Base
import uuid
from datetime import datetime

class User(Base):
    __tablename__ = "users"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(unique=True, index=True)
    password_hash: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(server_default=text("now()"))
