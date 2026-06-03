import uuid
from datetime import datetime
from sqlalchemy import String, Boolean, BigInteger, DateTime, func, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class File(Base):
	__tablename__ = "files"
	id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
	owner_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False, index=True)
	filename: Mapped[str] = mapped_column(String(1024), nullable=False)
	content_type: Mapped[str | None] = mapped_column(String(255), nullable=True)
	size: Mapped[int] = mapped_column(BigInteger, default=0)
	s3_key: Mapped[str] = mapped_column(String(2048), nullable=False, unique=True)
	is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)
	created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
	updated_at: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
