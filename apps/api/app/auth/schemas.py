from datetime import datetime
from uuid import UUID

from pydantic import EmailStr, Field

from app.core.schemas import ApiSchema
from app.db.models.user import UserRole


class SignupRequest(ApiSchema):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    name: str = Field(min_length=1, max_length=100)


class LoginRequest(ApiSchema):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


class UserResponse(ApiSchema):
    id: UUID
    email: EmailStr
    name: str
    role: UserRole
    created_at: datetime
    updated_at: datetime


class AuthResponse(ApiSchema):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
