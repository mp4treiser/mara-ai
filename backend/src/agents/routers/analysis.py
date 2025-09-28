from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any

from src.core.orm.database import get_async_session
from src.core.dependencies import get_current_user
from src.account.models.user import User
from src.account.services import SubscriptionService
from src.agents.schemas.analysis import TextAnalysisRequest, TextAnalysisResponse
from src.agents.services.agent_service import AgentService

router = APIRouter(prefix="/agents", tags=["agents"])

# Инициализируем сервисы
agent_service = AgentService()


@router.post("/{agent_id}/analyze", response_model=TextAnalysisResponse)
async def analyze_text(
    agent_id: int,
    request: TextAnalysisRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
):
    """
    Анализирует текст с помощью указанного агента.
    Требует активную подписку.
    """
    
    # Проверяем активную подписку
    subscription_service = SubscriptionService(session=db)
    active_subscriptions = await subscription_service.get_active_by_user_id(current_user.id)
    
    if not active_subscriptions:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Требуется активная подписка для использования агентов"
        )
    
    try:
        # Анализируем текст через агента
        result = await agent_service.analyze_text(
            agent_id=agent_id,
            user_id=current_user.id,
            text=request.text,
            db_session=db
        )
        
        if not result["success"]:
            return TextAnalysisResponse(
                agent_id=agent_id,
                response="",
                processing_time=result.get("processing_time", 0.0),
                documents_used=0,
                success=False,
                error_message=result.get("error_message", "Неизвестная ошибка")
            )
        
        return TextAnalysisResponse(
            agent_id=agent_id,
            response=result["response"],
            processing_time=result["processing_time"],
            documents_used=result["documents_used"],
            success=True
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при анализе текста: {str(e)}"
        )


@router.get("/{agent_id}/stats")
async def get_agent_stats(
    agent_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
):
    """
    Получает статистику агента.
    Требует активную подписку.
    """
    
    # Проверяем активную подписку
    subscription_service = SubscriptionService(session=db)
    active_subscriptions = await subscription_service.get_active_by_user_id(current_user.id)
    
    if not active_subscriptions:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Требуется активная подписка для использования агентов"
        )
    
    try:
        stats = agent_service.get_agent_stats(agent_id, current_user.id)
        return stats
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при получении статистики: {str(e)}"
        )


@router.get("/ollama/status")
async def check_ollama_status():
    """
    Проверяет статус подключения к Ollama.
    Доступно всем пользователям.
    """
    try:
        status = agent_service.test_ollama_connection()
        return {"status": "connected" if status else "disconnected"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
