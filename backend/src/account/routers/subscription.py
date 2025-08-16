from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from src.core.orm.database import get_async_session
from src.core.dependencies import get_current_user
from src.account.services.subscription import SubscriptionService
from src.account.schemas import CreateSubscriptionSchema, UpdateSubscriptionSchema, BaseSubscriptionSchema, SubscriptionWithDetailsSchema
from src.account.models import User

router = APIRouter(prefix="/subscriptions", tags=["subscriptions"])


@router.post("/", response_model=BaseSubscriptionSchema, status_code=status.HTTP_201_CREATED)
async def create_subscription(
    subscription_schema: CreateSubscriptionSchema,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
):
    """Создание новой подписки для текущего пользователя"""
    subscription_service = SubscriptionService(session=session)
    return await subscription_service.create_subscription(current_user.id, subscription_schema)


@router.get("/", response_model=list[BaseSubscriptionSchema])
async def get_all_subscriptions(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
):
    """Получение всех подписок (только для суперпользователей)"""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only superusers can view all subscriptions"
        )
    
    subscription_service = SubscriptionService(session=session)
    return await subscription_service.get_all()


@router.get("/my", response_model=list[BaseSubscriptionSchema])
async def get_my_subscriptions(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
):
    """Получение подписок текущего пользователя"""
    subscription_service = SubscriptionService(session=session)
    return await subscription_service.get_by_user_id(current_user.id)


@router.get("/my/active", response_model=list[BaseSubscriptionSchema])
async def get_my_active_subscriptions(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
):
    """Получение активных подписок текущего пользователя"""
    subscription_service = SubscriptionService(session=session)
    return await subscription_service.get_active_by_user_id(current_user.id)


@router.get("/{subscription_id}", response_model=BaseSubscriptionSchema)
async def get_subscription_by_id(
    subscription_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
):
    """Получение подписки по ID (пользователь может видеть только свои подписки)"""
    subscription_service = SubscriptionService(session=session)
    subscription = await subscription_service.get_by_id(subscription_id)
    
    # Проверяем, что пользователь может видеть эту подписку
    if not current_user.is_superuser and subscription.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view your own subscriptions"
        )
    
    return subscription


@router.get("/{subscription_id}/details", response_model=SubscriptionWithDetailsSchema)
async def get_subscription_details(
    subscription_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
):
    """Получение детальной информации о подписке"""
    subscription_service = SubscriptionService(session=session)
    details = await subscription_service.get_subscription_with_details(subscription_id)
    
    # Проверяем права доступа
    if not current_user.is_superuser and details["subscription"].user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view your own subscriptions"
        )
    
    return details


@router.put("/{subscription_id}", response_model=BaseSubscriptionSchema)
async def update_subscription(
    subscription_id: int,
    subscription_schema: UpdateSubscriptionSchema,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
):
    """Обновление подписки (только для суперпользователей)"""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only superusers can update subscriptions"
        )
    
    subscription_service = SubscriptionService(session=session)
    return await subscription_service.update(subscription_id, subscription_schema)


@router.delete("/{subscription_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_subscription(
    subscription_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
):
    """Удаление подписки (только для суперпользователей)"""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only superusers can delete subscriptions"
        )
    
    subscription_service = SubscriptionService(session=session)
    await subscription_service.delete(subscription_id)


@router.post("/deactivate-expired", status_code=status.HTTP_200_OK)
async def deactivate_expired_subscriptions(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
):
    """Деактивация истекших подписок (только для суперпользователей)"""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only superusers can deactivate expired subscriptions"
        )
    
    subscription_service = SubscriptionService(session=session)
    await subscription_service.deactivate_expired_subscriptions()
    return {"detail": "Expired subscriptions deactivated successfully"}
