from pydantic import BaseModel, Field
from typing import Optional


class BaseUserSchema(BaseModel):
    id: int
    email: str
    company: str | None
    first_name: str
    last_name: str
    is_active: bool | None = False


class UpdateUserSchema(BaseModel):
    email: Optional[str] = None
    company: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class CreateUserSchema(BaseModel):
    email: str
    password: str = Field(..., min_length=6, description="Пароль пользователя")
    company: str
    first_name: str
    last_name: str
