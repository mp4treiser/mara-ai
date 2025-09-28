from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.orm import selectinload
from datetime import datetime
from ..models.agent import Agent
from ..schemas.agent import AgentCreate, AgentUpdate


class AgentRepository:
    """Репозиторий для работы с агентами в БД"""
    
    def __init__(self, db_session: AsyncSession):
        self.db = db_session
    
    async def create(self, agent_data: AgentCreate, user_id: int) -> Agent:
        """Создает нового агента"""
        
        now = datetime.now()
        agent = Agent(
            name=agent_data.name,
            prompt=agent_data.prompt,
            user_id=user_id,
            is_active=True,
            created_at=now,
            updated_at=now
        )
        
        self.db.add(agent)
        await self.db.commit()
        await self.db.refresh(agent)
        
        return agent
    
    async def get_by_id(self, agent_id: int) -> Optional[Agent]:
        """Получает агента по ID"""
        result = await self.db.execute(
            select(Agent).where(Agent.id == agent_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_user_id(self, user_id: int) -> List[Agent]:
        """Получает всех агентов пользователя"""
        result = await self.db.execute(
            select(Agent).where(Agent.user_id == user_id)
        )
        return result.scalars().all()
    
    async def get_all(self) -> List[Agent]:
        """Получает всех агентов"""
        result = await self.db.execute(select(Agent))
        return result.scalars().all()
    
    async def update(self, agent_id: int, agent_data: AgentUpdate) -> Optional[Agent]:
        """Обновляет агента"""
        
        update_data = agent_data.model_dump(exclude_unset=True)
        update_data['updated_at'] = datetime.now()
        
        result = await self.db.execute(
            update(Agent)
            .where(Agent.id == agent_id)
            .values(**update_data)
            .returning(Agent)
        )
        
        await self.db.commit()
        return result.scalar_one_or_none()
    
    async def delete(self, agent_id: int) -> bool:
        """Удаляет агента"""
        result = await self.db.execute(
            delete(Agent).where(Agent.id == agent_id)
        )
        await self.db.commit()
        return result.rowcount > 0
    
    async def set_active_status(self, agent_id: int, is_active: bool) -> Optional[Agent]:
        """Устанавливает статус активности агента"""
        
        result = await self.db.execute(
            update(Agent)
            .where(Agent.id == agent_id)
            .values(is_active=is_active, updated_at=datetime.now())
            .returning(Agent)
)
        
        await self.db.commit()
        return result.scalar_one_or_none()
