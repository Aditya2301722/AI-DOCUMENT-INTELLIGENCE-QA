from sqlalchemy import DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime

from app.models.base import Base


class Session(Base):
    __tablename__ = "sessions"

    id: Mapped[int] = mapped_column(primary_key=True)

    customer_id: Mapped[int] = mapped_column(
        ForeignKey("customers.id"),
        nullable=False
    )

    started_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )

    ended_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True
    )

    customer = relationship("Customer")
