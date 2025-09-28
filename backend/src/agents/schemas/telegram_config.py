from datetime import datetime
from pydantic import BaseModel, Field, validator
from typing import Optional


class TelegramConfigCreate(BaseModel):
    bot_token: str = Field(..., min_length=10, description="Токен Telegram бота")
    chat_id: str = Field(..., min_length=1, description="ID чата для отправки сообщений")
    
    @validator('bot_token')
    def validate_bot_token(cls, v):
        if not v.startswith(('1', '2', '3', '4', '5', '6', '7', '8', '9')) and ':' not in v:
            raise ValueError('Неверный формат токена бота')
        return v.strip()
    
    @validator('chat_id')
    def validate_chat_id(cls, v):
        # Проверяем, что chat_id содержит только цифры (для личных чатов) или начинается с @ (для каналов)
        if not (v.replace('-', '').replace('_', '').isdigit() or v.startswith('@')):
            raise ValueError('Неверный формат ID чата')
        return v.strip()


class TelegramConfigUpdate(BaseModel):
    bot_token: Optional[str] = Field(None, min_length=10, description="Токен Telegram бота")
    chat_id: Optional[str] = Field(None, min_length=1, description="ID чата для отправки сообщений")
    is_active: Optional[bool] = Field(None, description="Активна ли интеграция")
    
    @validator('bot_token')
    def validate_bot_token(cls, v):
        if v is not None:
            if not v.startswith(('1', '2', '3', '4', '5', '6', '7', '8', '9')) and ':' not in v:
                raise ValueError('Неверный формат токена бота')
            return v.strip()
        return v
    
    @validator('chat_id')
    def validate_chat_id(cls, v):
        if v is not None:
            if not (v.replace('-', '').replace('_', '').isdigit() or v.startswith('@')):
                raise ValueError('Неверный формат ID чата')
            return v.strip()
        return v


class TelegramConfigResponse(BaseModel):
    id: int
    agent_id: int
    user_id: int
    bot_token: str  # Маскированный токен для безопасности
    chat_id: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
    
    @validator('bot_token', pre=True)
    def mask_token(cls, v):
        if isinstance(v, str) and len(v) > 10:
            return f"{v[:4]}...{v[-4:]}"
        return v


class TelegramTestMessage(BaseModel):
    message: str = Field(..., min_length=1, max_length=1000, description="Тестовое сообщение для отправки")


class TelegramSendMessage(BaseModel):
    message: str = Field(..., min_length=1, max_length=4000, description="Сообщение для отправки")
    parse_mode: Optional[str] = Field("HTML", description="Режим парсинга (HTML, Markdown)")
    disable_web_page_preview: Optional[bool] = Field(False, description="Отключить предварительный просмотр ссылок")
