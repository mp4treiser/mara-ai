from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from src.core.orm.database import get_async_session
from src.core.dependencies import get_current_user
from src.account.models.user import User
from src.agents.schemas.agent import AgentCreate, AgentUpdate, AgentResponse
from src.agents.services.agent_service import AgentService

router = APIRouter(prefix="/admin/agents", tags=["admin-agents"])

# Инициализируем сервис
agent_service = AgentService()


def check_admin_permissions(current_user: User):
    """Проверяет права администратора"""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Требуются права администратора"
        )


@router.post("/", response_model=AgentResponse)
async def create_agent(
    agent_data: AgentCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
):
    """Создает нового агента (только для админов)"""
    check_admin_permissions(current_user)
    
    try:
        # Создаем агента через сервис
        agent = await agent_service.create_agent(agent_data, current_user.id, db)
        
        if not agent:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Не удалось создать агента"
            )
        
        # Преобразуем в ответ
        return AgentResponse(
            id=agent.id,
            name=agent.name,
            prompt=agent.prompt,
            user_id=agent.user_id,
            is_active=agent.is_active,
            created_at=agent.created_at,
            updated_at=agent.updated_at
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при создании агента: {str(e)}"
        )


@router.get("/", response_model=List[AgentResponse])
async def list_agents(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
):
    """Получает список всех агентов (только для админов)"""
    check_admin_permissions(current_user)
    
    try:
        # Получаем агентов через сервис
        agents = await agent_service.get_all_agents(db)
        
        # Преобразуем в ответы
        return [
            AgentResponse(
                id=agent.id,
                name=agent.name,
                prompt=agent.prompt,
                user_id=agent.user_id,
                is_active=agent.is_active,
                created_at=agent.created_at,
                updated_at=agent.updated_at
            )
            for agent in agents
        ]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при получении списка агентов: {str(e)}"
        )


@router.get("/{agent_id}", response_model=AgentResponse)
async def get_agent(
    agent_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
):
    """Получает информацию об агенте (только для админов)"""
    check_admin_permissions(current_user)
    
    try:
        # Получаем агента через сервис
        agent = await agent_service._get_agent(agent_id, db)
        
        if not agent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Агент не найден"
            )
        
        # Преобразуем в ответ
        return AgentResponse(
            id=agent.id,
            name=agent.name,
            prompt=agent.prompt,
            user_id=agent.user_id,
            is_active=agent.is_active,
            created_at=agent.created_at,
            updated_at=agent.updated_at
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при получении агента: {str(e)}"
        )


@router.put("/{agent_id}", response_model=AgentResponse)
async def update_agent(
    agent_id: int,
    agent_data: AgentUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
):
    """Обновляет агента (только для админов)"""
    check_admin_permissions(current_user)
    
    try:
        # Обновляем агента через сервис
        agent = await agent_service.update_agent(agent_id, agent_data, db)
        
        if not agent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Агент не найден"
            )
        
        # Преобразуем в ответ
        return AgentResponse(
            id=agent.id,
            name=agent.name,
            prompt=agent.prompt,
            user_id=agent.user_id,
            is_active=agent.is_active,
            created_at=agent.created_at,
            updated_at=agent.updated_at
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при обновлении агента: {str(e)}"
        )


@router.delete("/{agent_id}")
async def delete_agent(
    agent_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
):
    """Удаляет агента (только для админов)"""
    check_admin_permissions(current_user)
    
    try:
        # Удаляем агента через сервис
        success = await agent_service.delete_agent(agent_id, db)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Агент не найден"
            )
        
        return {"message": "Агент успешно удален"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при удалении агента: {str(e)}"
        )
