from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any

from src.core.orm.database import get_async_session
from src.core.dependencies import get_current_user
from src.account.models.user import User
from src.agents.services.metrics_service import MetricsService

router = APIRouter(prefix="/metrics", tags=["metrics"])

# Инициализируем сервис
metrics_service = MetricsService()


def check_admin_permissions(current_user: User):
    """Проверяет права администратора"""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Требуются права администратора"
        )


@router.get("/agent/{agent_id}", response_model=Dict[str, Any])
async def get_agent_metrics(
    agent_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
):
    """Получает метрики использования агента (только для админов)"""
    check_admin_permissions(current_user)
    
    try:
        metrics = await metrics_service.get_agent_usage_stats(agent_id, db)
        return metrics
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при получении метрик агента: {str(e)}"
        )


@router.get("/user/{user_id}", response_model=Dict[str, Any])
async def get_user_metrics(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
):
    """Получает метрики использования агентов пользователем (только для админов)"""
    check_admin_permissions(current_user)
    
    try:
        metrics = await metrics_service.get_user_agent_usage_stats(user_id, db)
        return metrics
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при получении метрик пользователя: {str(e)}"
        )


@router.get("/my", response_model=Dict[str, Any])
async def get_my_metrics(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
):
    """Получает метрики использования агентов текущего пользователя"""
    try:
        metrics = await metrics_service.get_user_agent_usage_stats(current_user.id, db)
        return metrics
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при получении ваших метрик: {str(e)}"
        )


@router.get("/system", response_model=Dict[str, Any])
async def get_system_metrics(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
):
    """Получает общие метрики системы (только для админов)"""
    check_admin_permissions(current_user)
    
    try:
        metrics = await metrics_service.get_system_metrics(db)
        return metrics
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при получении системных метрик: {str(e)}"
        )


@router.get("/performance", response_model=Dict[str, Any])
async def get_performance_metrics(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
):
    """Получает метрики производительности (только для админов)"""
    check_admin_permissions(current_user)
    
    try:
        metrics = await metrics_service.get_performance_metrics(db)
        return metrics
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при получении метрик производительности: {str(e)}"
        )
