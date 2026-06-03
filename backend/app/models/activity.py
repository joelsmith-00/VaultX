import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, func, JSON
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class Activity(Base):
    __tablename__ = "activities"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    action: Mapped[str] = mapped_column(String(100), nullable=False)
    subject_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    subject_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    details: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
