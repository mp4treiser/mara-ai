from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload

from ..models.user_agent import UserAgent
from ..models.agent import Agent
from ..schemas.user_agent import UserAgentCreate, UserAgentUpdate


class UserAgentRepository:
    """Репозиторий для работы с UserAgent"""
    
    def __init__(self, db_session: AsyncSession):
        self.db = db_session
    
    async def create(self, user_agent_data: UserAgentCreate, user_id: int) -> Optional[UserAgent]:
        """Создает связь пользователя с агентом"""
        try:
            # Проверяем, что агент существует и активен
            agent = await self.db.execute(
                select(Agent).where(and_(Agent.id == user_agent_data.agent_id, Agent.is_active == True))
            )
            agent = agent.scalar_one_or_none()
            
            if not agent:
                return None
            
            # Проверяем, что связь уже не существует
            existing = await self.db.execute(
                select(UserAgent).where(
                    and_(UserAgent.user_id == user_id, UserAgent.agent_id == user_agent_data.agent_id)
                )
            )
            if existing.scalar_one_or_none():
                return None
            
            # Создаем связь
            user_agent = UserAgent(
                user_id=user_id,
                agent_id=user_agent_data.agent_id,
                is_active=True
            )
            
            self.db.add(user_agent)
            await self.db.commit()
            await self.db.refresh(user_agent)
            
            return user_agent
            
        except Exception as e:
            await self.db.rollback()
            raise e
    
    async def get_by_id(self, user_agent_id: int) -> Optional[UserAgent]:
        """Получает UserAgent по ID"""
        try:
            result = await self.db.execute(
                select(UserAgent).where(UserAgent.id == user_agent_id)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            raise e
    
    async def get_by_user_and_agent(self, user_id: int, agent_id: int) -> Optional[UserAgent]:
        """Получает UserAgent по пользователю и агенту"""
        try:
            result = await self.db.execute(
                select(UserAgent).where(
                    and_(UserAgent.user_id == user_id, UserAgent.agent_id == agent_id)
                )
            )
            return result.scalar_one_or_none()
        except Exception as e:
            raise e
    
    async def get_user_agents(self, user_id: int) -> List[UserAgent]:
        """Получает всех агентов пользователя"""
        try:
            result = await self.db.execute(
                select(UserAgent)
                .options(selectinload(UserAgent.agent))
                .where(and_(UserAgent.user_id == user_id, UserAgent.is_active == True))
            )
            return result.scalars().all()
        except Exception as e:
            raise e
    
    async def get_all_agents_with_user_status(self, user_id: int) -> List[dict]:
        """Получает всех агентов с информацией о том, подключен ли пользователь"""
        try:
            # Получаем всех активных агентов
            agents_result = await self.db.execute(
                select(Agent).where(Agent.is_active == True)
            )
            agents = agents_result.scalars().all()
            
            # Получаем агентов пользователя
            user_agents_result = await self.db.execute(
                select(UserAgent).where(UserAgent.user_id == user_id)
            )
            user_agents = {ua.agent_id: ua for ua in user_agents_result.scalars().all()}
            
            # Формируем результат
            result = []
            for agent in agents:
                user_agent = user_agents.get(agent.id)
                result.append({
                    'id': agent.id,
                    'name': agent.name,
                    'prompt': agent.prompt,
                    'is_active': agent.is_active,
                    'created_at': agent.created_at,
                    'updated_at': agent.updated_at,
                    'user_agent_id': user_agent.id if user_agent else None,
                    'is_user_agent': user_agent is not None
                })
            
            return result
            
        except Exception as e:
            raise e
    
    async def update(self, user_agent_id: int, user_agent_data: UserAgentUpdate) -> Optional[UserAgent]:
        """Обновляет UserAgent"""
        try:
            user_agent = await self.get_by_id(user_agent_id)
            if not user_agent:
                return None
            
            # Обновляем поля
            for field, value in user_agent_data.dict(exclude_unset=True).items():
                setattr(user_agent, field, value)
            
            await self.db.commit()
            await self.db.refresh(user_agent)
            
            return user_agent
            
        except Exception as e:
            await self.db.rollback()
            raise e
    
    async def delete(self, user_agent_id: int) -> bool:
        """Удаляет связь пользователя с агентом"""
        try:
            user_agent = await self.get_by_id(user_agent_id)
            if not user_agent:
                return False
            
            await self.db.delete(user_agent)
            await self.db.commit()
            
            return True
            
        except Exception as e:
            await self.db.rollback()
            raise e
    
    async def deactivate(self, user_agent_id: int) -> bool:
        """Деактивирует связь пользователя с агентом"""
        try:
            user_agent = await self.get_by_id(user_agent_id)
            if not user_agent:
                return False
            
            user_agent.is_active = False
            await self.db.commit()
            
            return True
            
        except Exception as e:
            await self.db.rollback()
            raise e
