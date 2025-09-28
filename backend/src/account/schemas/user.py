from pydantic import BaseModel, Field
from typing import Optional


class BaseUserSchema(BaseModel):
    id: int
    email: str
    company: str | None
    first_name: str
    last_name: str
    is_active: bool | None = False
    is_superuser: bool | None = False
    balance: float | None = 0.0

    class Config:
        from_attributes = True


class UpdateUserSchema(BaseModel):
    email: Optional[str] = None
    company: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_active: Optional[bool] = None
    is_superuser: Optional[bool] = None


class CreateUserSchema(BaseModel):
    email: str
    password: str = Field(..., min_length=6, description="Пароль пользователя")
    company: str
    first_name: str
    last_name: str
    is_superuser: bool = False

class UserBalanceResponse(BaseModel):
    balance: float
    currency: str = "USD"
    user_id: int


class UserProfileResponse(BaseModel):
    id: int
    email: str
    first_name: str
    last_name: str
    company: str
    is_active: bool
    balance: float
    is_superuser: bool

    class Config:
        from_attributes = True