from pydantic import BaseModel
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
    company: str
    first_name: str
    last_name: str
