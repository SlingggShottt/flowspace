from pydantic import BaseModel, EmailStr, field_validator
from app.schemas.user import UserResponse


class RegisterRequest(BaseModel):
    company_name: str
    email: EmailStr
    password: str
    name: str

    @field_validator("password")
    @classmethod
    def password_length(cls, v: str) -> str:
        if len(v.encode("utf-8")) > 72:
            raise ValueError("Password must be 72 characters or fewer")
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        return v


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class RefreshRequest(BaseModel):
    refresh_token: str