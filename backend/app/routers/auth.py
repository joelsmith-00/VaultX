from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.user import (
    UserRegisterRequest,
    UserLoginRequest,
    TokenResponse,
    RefreshTokenRequest,
    PasswordResetRequest,
    PasswordResetConfirmRequest,
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
async def register(payload: UserRegisterRequest, response: Response, db: AsyncSession = Depends(get_db)):
    # check duplicates
    q = select(User).where((User.email == payload.email) | (User.username == payload.username))
    r = await db.execute(q)
    existing = r.scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email or username already registered")
    user = await create_user(db, payload.email, payload.username, payload.password)
    access, refresh = await create_tokens_for_user(db, user)
    # set httpOnly refresh cookie
    secure = False if settings.ENVIRONMENT == "development" else True
    response.set_cookie(
        key="vaultx_refresh",
        value=refresh,
        httponly=True,
        secure=secure,
        samesite="lax",
        path="/api/auth",
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 3600,
    )
    return TokenResponse(access_token=access, refresh_token=refresh, expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60)


@router.post("/api/auth/login", response_model=TokenResponse)
async def login(payload: UserLoginRequest, response: Response, db: AsyncSession = Depends(get_db)):
    user = await authenticate_user(db, payload.email, payload.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    access, refresh = await create_tokens_for_user(db, user)
    secure = False if settings.ENVIRONMENT == "development" else True
    response.set_cookie(
        key="vaultx_refresh",
        value=refresh,
        httponly=True,
        secure=secure,
        samesite="lax",
        path="/api/auth",
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 3600,
    )
    return TokenResponse(access_token=access, refresh_token=refresh, expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60)


@router.post("/api/auth/refresh", response_model=TokenResponse)
async def refresh(request: Request, payload: RefreshTokenRequest, response: Response, db: AsyncSession = Depends(get_db)):
    # allow refresh token from cookie if not provided in body
    token = payload.refresh_token or request.cookies.get("vaultx_refresh")
    if not token:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing refresh token")
    result = await rotate_refresh_token(db, token)
    if not result:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
    access, refresh = result
    secure = False if settings.ENVIRONMENT == "development" else True
    response.set_cookie(
        key="vaultx_refresh",
        value=refresh,
        httponly=True,
        secure=secure,
        samesite="lax",
        path="/api/auth",
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 3600,
    )
    return TokenResponse(access_token=access, refresh_token=refresh, expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60)


@router.post("/api/auth/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(request: Request, payload: RefreshTokenRequest, response: Response, db: AsyncSession = Depends(get_db)):
    token = payload.refresh_token or request.cookies.get("vaultx_refresh")
    if not token:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing refresh token")
    ok = await revoke_refresh_token(db, token)
    # clear cookie regardless
    response.delete_cookie("vaultx_refresh", path="/api/auth")
    if not ok:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token or already revoked")
    return None


@router.post("/api/auth/password-reset", status_code=status.HTTP_202_ACCEPTED)
async def password_reset_request(payload: PasswordResetRequest, db: AsyncSession = Depends(get_db)):
    # send password reset email if user exists
    await __import__("app.services").services.auth_service.send_password_reset(db, payload.email)
    # respond generically
    return {"message": "If an account with that email exists, a reset link has been sent."}


@router.post("/api/auth/password-reset/confirm", status_code=status.HTTP_200_OK)
async def password_reset_confirm(payload: PasswordResetConfirmRequest, db: AsyncSession = Depends(get_db)):
    ok = await __import__("app.services").services.auth_service.confirm_password_reset(db, payload.token, payload.new_password)
    if not ok:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired token")
    return {"message": "Password has been reset."}
