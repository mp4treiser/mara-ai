from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.orm import selectinload
from datetime import datetime

from ..models.telegram_monitored_chat import TelegramMonitoredChat
from ..models.telegram_config import TelegramConfig
from ..schemas.telegram_monitored_chat import TelegramMonitoredChatCreate, TelegramMonitoredChatUpdate
import json


class TelegramMonitoredChatRepository:
    """Репозиторий для работы с мониторингом Telegram чатов"""
    
    def __init__(self, db_session: AsyncSession):
        self.db = db_session
    
    async def create(self, config_id: int, chat_data: TelegramMonitoredChatCreate) -> TelegramMonitoredChat:
        """Создает новый мониторинг чата"""
        from datetime import datetime
        
        # Преобразуем keywords в JSON строку
        keywords_json = json.dumps(chat_data.keywords) if chat_data.keywords else None
        
        chat = TelegramMonitoredChat(
            telegram_config_id=config_id,
            chat_id=chat_data.chat_id,
            chat_title=chat_data.chat_title,
            chat_type=chat_data.chat_type,
            keywords=keywords_json,
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        self.db.add(chat)
        await self.db.commit()
        await self.db.refresh(chat)
        
        return chat
    
    async def get_by_id(self, chat_id: int) -> Optional[TelegramMonitoredChat]:
        """Получает мониторинг чата по ID"""
        result = await self.db.execute(
            select(TelegramMonitoredChat).where(TelegramMonitoredChat.id == chat_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_config_id(self, config_id: int) -> List[TelegramMonitoredChat]:
        """Получает все мониторинги чатов для конфигурации"""
        result = await self.db.execute(
            select(TelegramMonitoredChat)
            .where(TelegramMonitoredChat.telegram_config_id == config_id)
            .order_by(TelegramMonitoredChat.created_at.desc())
        )
        return result.scalars().all()
    
    async def get_active_by_config_id(self, config_id: int) -> List[TelegramMonitoredChat]:
        """Получает активные мониторинги чатов для конфигурации"""
        result = await self.db.execute(
            select(TelegramMonitoredChat)
            .where(
                TelegramMonitoredChat.telegram_config_id == config_id,
                TelegramMonitoredChat.is_active == True
            )
            .order_by(TelegramMonitoredChat.created_at.desc())
        )
        return result.scalars().all()
    
    async def get_by_chat_id(self, chat_id: str) -> List[TelegramMonitoredChat]:
        """Получает все мониторинги для конкретного чата"""
        result = await self.db.execute(
            select(TelegramMonitoredChat)
            .options(selectinload(TelegramMonitoredChat.telegram_config))
            .where(TelegramMonitoredChat.chat_id == chat_id)
        )
        return result.scalars().all()
    
    async def update(self, chat_id: int, chat_data: TelegramMonitoredChatUpdate) -> Optional[TelegramMonitoredChat]:
        """Обновляет мониторинг чата"""
        
        update_data = {}
        if chat_data.chat_title is not None:
            update_data['chat_title'] = chat_data.chat_title
        if chat_data.chat_type is not None:
            update_data['chat_type'] = chat_data.chat_type
        if chat_data.is_active is not None:
            update_data['is_active'] = chat_data.is_active
        if chat_data.keywords is not None:
            update_data['keywords'] = json.dumps(chat_data.keywords)
        
        if update_data:
            update_data['updated_at'] = datetime.utcnow()
            
            result = await self.db.execute(
                update(TelegramMonitoredChat)
                .where(TelegramMonitoredChat.id == chat_id)
                .values(**update_data)
                .returning(TelegramMonitoredChat)
            )
            
            await self.db.commit()
            return result.scalar_one_or_none()
        
        return await self.get_by_id(chat_id)
    
    async def delete(self, chat_id: int) -> bool:
        """Удаляет мониторинг чата"""
        result = await self.db.execute(
            delete(TelegramMonitoredChat).where(TelegramMonitoredChat.id == chat_id)
        )
        await self.db.commit()
        return result.rowcount > 0
    
    async def delete_by_config_id(self, config_id: int) -> int:
        """Удаляет все мониторинги чатов для конфигурации"""
        result = await self.db.execute(
            delete(TelegramMonitoredChat).where(TelegramMonitoredChat.telegram_config_id == config_id)
        )
        await self.db.commit()
        return result.rowcount
    
    async def get_all_active_monitored_chats(self) -> List[TelegramMonitoredChat]:
        """Получает все активные мониторинги чатов (для webhook)"""
        result = await self.db.execute(
            select(TelegramMonitoredChat)
            .options(
                selectinload(TelegramMonitoredChat.telegram_config)
                .selectinload(TelegramConfig.agent)
            )
            .where(TelegramMonitoredChat.is_active == True)
        )
        return result.scalars().all()
