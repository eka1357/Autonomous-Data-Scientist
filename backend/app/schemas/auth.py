from uuid import UUID
from pydantic import BaseModel, EmailStr, Field


class UserRegisterRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)


class UserRegisterResponseData(BaseModel):
    user_id: UUID
    message: str = "Account created successfully"


class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponseData(BaseModel):
    access_token: str
    refresh_token: str
    expires_in: int


class TokenRefreshRequest(BaseModel):
    refresh_token: str
