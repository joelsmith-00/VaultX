import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Boolean, DateTime, func, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    token_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    revoked: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    expires_at: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    replaced_by: Mapped[str | None] = mapped_column(String(36), ForeignKey("refresh_tokens.id"), nullable=True)
