from sqlalchemy import DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime

from app.models.base import Base


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(primary_key=True)

    session_id: Mapped[int] = mapped_column(
        ForeignKey("sessions.id"),
        nullable=False
    )

    sender: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    content: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )

    session = relationship("Session")
