from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.user import (
    UserRegisterRequest,
    UserLoginRequest,
    TokenResponse,
    RefreshTokenRequest,
)
from app.services import (
    create_user,
    authenticate_user,
    create_tokens_for_user,
    rotate_refresh_token,
    revoke_refresh_token,
)
from app.models.user import User
from app.config import settings

router = APIRouter(tags=["Auth"], prefix="")


@router.post("/api/auth/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(payload: UserRegisterRequest, db: AsyncSession = Depends(get_db)):
    # check duplicates
    q = select(User).where((User.email == payload.email) | (User.username == payload.username))
    r = await db.execute(q)
    existing = r.scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email or username already registered")
    user = await create_user(db, payload.email, payload.username, payload.password)
    access, refresh = await create_tokens_for_user(db, user)
    return TokenResponse(access_token=access, refresh_token=refresh, expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60)


@router.post("/api/auth/login", response_model=TokenResponse)
async def login(payload: UserLoginRequest, db: AsyncSession = Depends(get_db)):
    user = await authenticate_user(db, payload.email, payload.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    access, refresh = await create_tokens_for_user(db, user)
    return TokenResponse(access_token=access, refresh_token=refresh, expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60)


@router.post("/api/auth/refresh", response_model=TokenResponse)
async def refresh(payload: RefreshTokenRequest, db: AsyncSession = Depends(get_db)):
    result = await rotate_refresh_token(db, payload.refresh_token)
    if not result:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
    access, refresh = result
    return TokenResponse(access_token=access, refresh_token=refresh, expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60)


@router.post("/api/auth/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(payload: RefreshTokenRequest, db: AsyncSession = Depends(get_db)):
    ok = await revoke_refresh_token(db, payload.refresh_token)
    if not ok:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token or already revoked")
    return None
