from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.orm import selectinload
from datetime import datetime

from ..models.telegram_config import TelegramConfig
from ..schemas.telegram_config import TelegramConfigCreate, TelegramConfigUpdate


class TelegramConfigRepository:
    """Репозиторий для работы с Telegram конфигурациями в БД"""
    
    def __init__(self, db_session: AsyncSession):
        self.db = db_session
    
    async def create(self, config_data: TelegramConfigCreate, agent_id: int, user_id: int) -> TelegramConfig:
        """Создает новую Telegram конфигурацию"""
        
        config = TelegramConfig(
            agent_id=agent_id,
            user_id=user_id,
            bot_token=config_data.bot_token,
            chat_id=config_data.chat_id,
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        self.db.add(config)
        await self.db.commit()
        await self.db.refresh(config)
        
        return config
    
    async def get_by_id(self, config_id: int) -> Optional[TelegramConfig]:
        """Получает конфигурацию по ID"""
        result = await self.db.execute(
            select(TelegramConfig).where(TelegramConfig.id == config_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_agent_id(self, agent_id: int) -> Optional[TelegramConfig]:
        """Получает конфигурацию по ID агента"""
        result = await self.db.execute(
            select(TelegramConfig)
            .options(selectinload(TelegramConfig.agent))
            .where(TelegramConfig.agent_id == agent_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_user_and_agent(self, user_id: int, agent_id: int) -> Optional[TelegramConfig]:
        """Получает конфигурацию по пользователю и агенту"""
        result = await self.db.execute(
            select(TelegramConfig)
            .where(
                TelegramConfig.user_id == user_id,
                TelegramConfig.agent_id == agent_id
            )
        )
        return result.scalar_one_or_none()
    
    async def get_by_agent_id_and_user_id(self, agent_id: int, user_id: int) -> Optional[TelegramConfig]:
        """Получает конфигурацию по ID агента и пользователя"""
        result = await self.db.execute(
            select(TelegramConfig)
            .where(
                TelegramConfig.agent_id == agent_id,
                TelegramConfig.user_id == user_id
            )
        )
        return result.scalar_one_or_none()
    
    async def get_by_bot_token(self, bot_token: str) -> Optional[TelegramConfig]:
        """Получает конфигурацию по токену бота"""
        result = await self.db.execute(
            select(TelegramConfig)
            .where(TelegramConfig.bot_token == bot_token)
        )
        return result.scalar_one_or_none()
    
    async def get_all_active_configs(self) -> List[TelegramConfig]:
        """Получает все активные конфигурации"""
        result = await self.db.execute(
            select(TelegramConfig)
            .where(TelegramConfig.is_active == True)
        )
        return result.scalars().all()
    
    async def get_by_user_id(self, user_id: int) -> List[TelegramConfig]:
        """Получает все конфигурации пользователя"""
        result = await self.db.execute(
            select(TelegramConfig)
            .options(selectinload(TelegramConfig.agent))
            .where(TelegramConfig.user_id == user_id)
        )
        return result.scalars().all()
    
    async def update(self, config_id: int, config_data: TelegramConfigUpdate) -> Optional[TelegramConfig]:
        """Обновляет конфигурацию"""
        
        update_data = {}
        if config_data.bot_token is not None:
            update_data['bot_token'] = config_data.bot_token
        if config_data.chat_id is not None:
            update_data['chat_id'] = config_data.chat_id
        if config_data.is_active is not None:
            update_data['is_active'] = config_data.is_active
        
        if not update_data:
            return await self.get_by_id(config_id)
        
        update_data['updated_at'] = datetime.utcnow()
        
        result = await self.db.execute(
            update(TelegramConfig)
            .where(TelegramConfig.id == config_id)
            .values(**update_data)
            .returning(TelegramConfig)
        )
        
        await self.db.commit()
        return result.scalar_one_or_none()
    
    async def delete(self, config_id: int) -> bool:
        """Удаляет конфигурацию"""
        result = await self.db.execute(
            delete(TelegramConfig).where(TelegramConfig.id == config_id)
        )
        await self.db.commit()
        return result.rowcount > 0
    
    async def delete_by_user(self, config_id: int, user_id: int) -> bool:
        """Удаляет конфигурацию с проверкой владельца"""
        result = await self.db.execute(
            delete(TelegramConfig).where(
                TelegramConfig.id == config_id,
                TelegramConfig.user_id == user_id
            )
        )
        await self.db.commit()
        return result.rowcount > 0
    
    async def delete_by_agent(self, agent_id: int) -> bool:
        """Удаляет конфигурацию агента"""
        result = await self.db.execute(
            delete(TelegramConfig).where(TelegramConfig.agent_id == agent_id)
        )
        await self.db.commit()
        return result.rowcount > 0
    
    async def get_active_configs(self) -> List[TelegramConfig]:
        """Получает все активные конфигурации"""
        result = await self.db.execute(
            select(TelegramConfig)
            .options(selectinload(TelegramConfig.agent))
            .where(TelegramConfig.is_active == True)
        )
        return result.scalars().all()
    
    async def get_active_configs_by_user(self, user_id: int) -> List[TelegramConfig]:
        """Получает активные конфигурации пользователя"""
        result = await self.db.execute(
            select(TelegramConfig)
            .options(selectinload(TelegramConfig.agent))
            .where(
                TelegramConfig.user_id == user_id,
                TelegramConfig.is_active == True
            )
        )
        return result.scalars().all()
