from datetime import datetime
from pydantic import BaseModel, Field, validator
from typing import Optional, List
import json


class TelegramMonitoredChatCreate(BaseModel):
    chat_id: str = Field(..., min_length=1, description="ID чата для мониторинга")
    chat_title: Optional[str] = Field(None, description="Название чата")
    chat_type: str = Field(..., description="Тип чата (group, supergroup, channel)")
    keywords: Optional[List[str]] = Field(None, description="Ключевые слова для фильтрации")
    
    @validator('chat_id')
    def validate_chat_id(cls, v):
        # Проверяем, что chat_id содержит только цифры (для личных чатов) или начинается с @ (для каналов)
        if not (v.replace('-', '').replace('_', '').isdigit() or v.startswith('@')):
            raise ValueError('Неверный формат ID чата')
        return v.strip()
    
    @validator('chat_type')
    def validate_chat_type(cls, v):
        allowed_types = ['group', 'supergroup', 'channel', 'private']
        if v not in allowed_types:
            raise ValueError(f'Тип чата должен быть одним из: {", ".join(allowed_types)}')
        return v


class TelegramMonitoredChatUpdate(BaseModel):
    chat_title: Optional[str] = Field(None, description="Название чата")
    chat_type: Optional[str] = Field(None, description="Тип чата")
    is_active: Optional[bool] = Field(None, description="Активен ли мониторинг")
    keywords: Optional[List[str]] = Field(None, description="Ключевые слова для фильтрации")
    
    @validator('chat_type')
    def validate_chat_type(cls, v):
        if v is not None:
            allowed_types = ['group', 'supergroup', 'channel', 'private']
            if v not in allowed_types:
                raise ValueError(f'Тип чата должен быть одним из: {", ".join(allowed_types)}')
        return v


class TelegramMonitoredChatResponse(BaseModel):
    id: int
    telegram_config_id: int
    chat_id: str
    chat_title: Optional[str]
    chat_type: str
    is_active: bool
    keywords: Optional[List[str]]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
    
    @validator('keywords', pre=True)
    def parse_keywords(cls, v):
        if isinstance(v, str):
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                return []
        return v or []


class TelegramWebhookMessage(BaseModel):
    """Схема для входящих сообщений от Telegram webhook"""
    update_id: int
    message: Optional[dict] = None
    edited_message: Optional[dict] = None
    channel_post: Optional[dict] = None
    edited_channel_post: Optional[dict] = None


class TelegramAlertAnalysis(BaseModel):
    """Схема для анализа алерта"""
    chat_id: str
    message_text: str
    message_id: int
    from_user: Optional[dict] = None
    chat_info: Optional[dict] = None
    timestamp: datetime
