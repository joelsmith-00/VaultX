from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional
from datetime import datetime
import re

class UserRegisterRequest(BaseModel):
    email: EmailStr
    username: str
    password: str

    @field_validator('username')
    @classmethod
    def username_valid(cls, v):
        if not re.match(r'^[a-zA-Z0-9_]{3,30}$', v):
            raise ValueError('Username must be 3-30 chars, letters/numbers/underscore only')
        return v

    @field_validator('password')
    @classmethod
    def password_strong(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain an uppercase letter')
        if not re.search(r'[0-9]', v):
            raise ValueError('Password must contain a number')
        return v

class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = 900

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class UserResponse(BaseModel):
    id: str
    email: str
    username: str
    avatar_url: Optional[str] = None
    is_verified: bool
    storage_used: int
    storage_limit: int
    created_at: datetime
    model_config = {"from_attributes": True}

class UserUpdateRequest(BaseModel):
    username: Optional[str] = None
    avatar_url: Optional[str] = None

class PasswordResetRequest(BaseModel):
    email: EmailStr

class PasswordResetConfirmRequest(BaseModel):
    token: str
    new_password: str
