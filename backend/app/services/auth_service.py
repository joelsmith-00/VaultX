"""Authentication service: user creation, authentication, and refresh token handling."""
from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple

from sqlalchemy import select, delete, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.refresh_token import RefreshToken
from app.utils import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    create_reset_token,
    decode_token,
)
from app.services.email_service import send_password_reset_email


async def create_user(db: AsyncSession, email: str, username: str, password: str) -> User:
    hashed = hash_password(password)
    user = User(email=email, username=username, password_hash=hashed)
    db.add(user)
    await db.flush()
    return user


async def authenticate_user(db: AsyncSession, email: str, password: str) -> Optional[User]:
    q = select(User).where(User.email == email)
    r = await db.execute(q)
    user = r.scalar_one_or_none()
    if not user or not user.password_hash:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user


def _token_payload_for_user(user: User) -> dict:
    return {"sub": user.id, "email": user.email}


async def create_tokens_for_user(db: AsyncSession, user: User) -> Tuple[str, str]:
    payload = _token_payload_for_user(user)
    access = create_access_token(payload)
    refresh = create_refresh_token(payload)
    # store hashed refresh token
    token_hash = hash_password(refresh)
    rt = RefreshToken(token_hash=token_hash, user_id=user.id, expires_at=(datetime.now(timezone.utc) + timedelta(days=7)))
    db.add(rt)
    await db.flush()
    return access, refresh


async def find_refresh_token_record(db: AsyncSession, raw_refresh_token: str) -> Optional[RefreshToken]:
    # Decode to get user id, then check that token hash matches one of the user's tokens
    payload = decode_token(raw_refresh_token)
    if not payload or payload.get("type") != "refresh":
        return None
    user_id = payload.get("sub")
    if not user_id:
        return None
    q = select(RefreshToken).where(RefreshToken.user_id == user_id, RefreshToken.revoked == False)
    r = await db.execute(q)
    candidates = r.scalars().all()
    for cand in candidates:
        if verify_password(raw_refresh_token, cand.token_hash):
            return cand
    return None


async def rotate_refresh_token(db: AsyncSession, raw_refresh_token: str) -> Optional[Tuple[str, str]]:
    rec = await find_refresh_token_record(db, raw_refresh_token)
    if not rec:
        return None
    # revoke old
    rec.revoked = True
    await db.flush()
    # create new tokens
    # fetch user
    q = select(User).where(User.id == rec.user_id)
    r = await db.execute(q)
    user = r.scalar_one_or_none()
    if not user:
        return None
    access = create_access_token({"sub": user.id, "email": user.email})
    new_refresh = create_refresh_token({"sub": user.id, "email": user.email})
    new_hash = hash_password(new_refresh)
    new_rec = RefreshToken(token_hash=new_hash, user_id=user.id, expires_at=(datetime.now(timezone.utc) + timedelta(days=7)), replaced_by=rec.id)
    db.add(new_rec)
    await db.flush()
    return access, new_refresh


async def revoke_refresh_token(db: AsyncSession, raw_refresh_token: str) -> bool:
    rec = await find_refresh_token_record(db, raw_refresh_token)
    if not rec:
        return False
    rec.revoked = True
    await db.flush()
    return True


async def revoke_all_user_refresh_tokens(db: AsyncSession, user_id: str) -> int:
    q = update(RefreshToken).where(RefreshToken.user_id == user_id).values(revoked=True)
    await db.execute(q)
    await db.flush()
    return 1


async def send_password_reset(db: AsyncSession, email: str) -> bool:
    q = select(User).where(User.email == email)
    r = await db.execute(q)
    user = r.scalar_one_or_none()
    if not user:
        # Don't reveal whether the email exists; behave as if sent
        return False
    payload = {"sub": user.id, "email": user.email}
    token = create_reset_token(payload)
    # Send email (synchronous); that's acceptable for now
    send_password_reset_email(user.email, token, user.username)
    return True


async def confirm_password_reset(db: AsyncSession, token: str, new_password: str) -> bool:
    payload = decode_token(token)
    if not payload or payload.get("type") != "reset":
        return False
    user_id = payload.get("sub")
    if not user_id:
        return False
    q = select(User).where(User.id == user_id)
    r = await db.execute(q)
    user = r.scalar_one_or_none()
    if not user:
        return False
    user.password_hash = hash_password(new_password)
    await db.flush()
    return True
