import uuid
from sqlalchemy import String, Boolean, BigInteger, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base

class User(Base):
	__tablename__ = "users"
	id: Mapped[str] = mapped_column(String(36), primary_key=True, 
		default=lambda: str(uuid.uuid4()))
	email: Mapped[str] = mapped_column(String(255), unique=True, 
		nullable=False, index=True)
	username: Mapped[str] = mapped_column(String(50), unique=True, 
		nullable=False, index=True)
	password_hash: Mapped[str | None] = mapped_column(String(255), nullable=True)
	google_id: Mapped[str | None] = mapped_column(String(255), 
		unique=True, nullable=True)
	avatar_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
	is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
	is_active: Mapped[bool] = mapped_column(Boolean, default=True)
	totp_secret: Mapped[str | None] = mapped_column(String(255), nullable=True)
	totp_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
	storage_used: Mapped[int] = mapped_column(BigInteger, default=0)
	storage_limit: Mapped[int] = mapped_column(BigInteger, default=5368709120)
	created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), 
		server_default=func.now())
	updated_at: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True), 
		onupdate=func.now(), nullable=True)