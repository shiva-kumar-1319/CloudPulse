from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, ConfigDict


class UserRegisterRequest(BaseModel):
    username: str = Field(min_length=3, max_length=50, description="Unique username")
    email: EmailStr = Field(description="Valid email address")
    password: str = Field(min_length=6, description="Password (at least 6 chars)")


class UserLoginRequest(BaseModel):
    username: str = Field(description="Account username")
    password: str = Field(description="Account password")


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    username: str
    email: EmailStr
    is_active: bool = True
    role: str = "user"
    created_at: datetime


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int = 3600
    user_id: str
    username: str


class TokenVerifyRequest(BaseModel):
    token: str = Field(description="JWT token string to verify")


class TokenVerifyResponse(BaseModel):
    valid: bool
    user_id: Optional[str] = None
    username: Optional[str] = None
    role: Optional[str] = None
    expires_at: Optional[datetime] = None
