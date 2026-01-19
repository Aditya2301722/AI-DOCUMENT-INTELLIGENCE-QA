from sqlalchemy import String, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime

from app.models.base import Base


class Customer(Base):
    __tablename__ = "customers"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    preferred_language: Mapped[str] = mapped_column(String(5), default="en")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
