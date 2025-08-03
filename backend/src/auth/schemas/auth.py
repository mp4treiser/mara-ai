from pydantic import BaseModel, EmailStr, Field


class LoginSchema(BaseModel):
    email: EmailStr = Field(..., description="Email пользователя")
    password: str = Field(..., min_length=6, description="Пароль")


class RegisterSchema(BaseModel):
    email: EmailStr = Field(..., description="Email пользователя")
    password: str = Field(..., min_length=6, description="Пароль")
    confirm_password: str = Field(..., description="Подтверждение пароля")
    company: str = Field(..., min_length=1, description="Название компании")
    first_name: str = Field(..., min_length=1, description="Имя")
    last_name: str = Field(..., min_length=1, description="Фамилия")


class TokenSchema(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class UserResponseSchema(BaseModel):
    id: int
    email: str
    company: str
    first_name: str
    last_name: str
    is_active: bool
