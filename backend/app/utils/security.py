"""VaultX - Security and token helpers."""

from datetime import datetime, timedelta, timezone
import secrets
from typing import Any

from jose import JWTError, jwt
from passlib.context import CryptContext
import pyotp

from app.config import settings

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


def hash_password(password: str) -> str:
	"""Hash a plaintext password."""
	return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
	"""Verify a plaintext password against a hash."""
	return pwd_context.verify(plain_password, hashed_password)


def _create_token(payload: dict[str, Any], expires_delta: timedelta, token_type: str) -> str:
	now = datetime.now(timezone.utc)
	data = payload.copy()
	data.update({
		"type": token_type,
		"iat": int(now.timestamp()),
		"exp": int((now + expires_delta).timestamp()),
	})
	return jwt.encode(data, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def create_access_token(payload: dict[str, Any], expires_delta: timedelta | None = None) -> str:
	"""Create a signed access token."""
	expires = expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
	return _create_token(payload, expires, "access")


def create_refresh_token(payload: dict[str, Any], expires_delta: timedelta | None = None) -> str:
	"""Create a signed refresh token."""
	expires = expires_delta or timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
	return _create_token(payload, expires, "refresh")


def create_reset_token(payload: dict[str, Any], expires_delta: timedelta | None = None) -> str:
	"""Create a short-lived password reset token."""
	expires = expires_delta or timedelta(minutes=30)
	return _create_token(payload, expires, "reset")


def decode_token(token: str) -> dict[str, Any] | None:
	"""Decode and validate a JWT payload."""
	try:
		return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
	except JWTError:
		return None


def generate_verification_token(length: int = 32) -> str:
	"""Generate a secure URL-safe verification token."""
	return secrets.token_urlsafe(length)


def generate_totp_secret(length: int = 32) -> str:
	"""Generate a TOTP shared secret."""
	return pyotp.random_base32(length=length)