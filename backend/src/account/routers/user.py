from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.orm.database import get_async_session
from src.core.dependencies import get_current_user
from src.account.models.user import User
from src.account.services.user import UserService
from src.account.schemas.user import UserBalanceResponse, UserProfileResponse
from pydantic import BaseModel
from typing import Optional

router = APIRouter(prefix="/user", tags=["user"])


@router.get("/balance", response_model=UserBalanceResponse)
async def get_user_balance(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
):
    """Получает баланс текущего пользователя"""
    try:
        return UserBalanceResponse(
            balance=float(current_user.balance),
            user_id=current_user.id
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при получении баланса: {str(e)}"
        )


@router.get("/me/profile", response_model=UserProfileResponse)
async def get_user_profile(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
):
    """Получает профиль текущего пользователя"""
    try:
        return UserProfileResponse(
            id=current_user.id,
            email=current_user.email,
            first_name=current_user.first_name or "",
            last_name=current_user.last_name or "",
            company=current_user.company or "",
            is_active=current_user.is_active,
            balance=float(current_user.balance),
            is_superuser=current_user.is_superuser
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при получении профиля: {str(e)}"
        )


@router.put("/profile")
async def update_user_profile(
    profile_data: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
):
    """Обновляет профиль пользователя"""
    try:
        user_service = UserService(session=db)
        
        # Разрешенные поля для обновления
        allowed_fields = ["first_name", "last_name", "company"]
        update_data = {k: v for k, v in profile_data.items() if k in allowed_fields}
        
        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Нет данных для обновления"
            )
        
        updated_user = await user_service.update_profile(current_user.id, update_data)
        
        return UserProfileResponse(
            id=updated_user.id,
            email=updated_user.email,
            first_name=updated_user.first_name or "",
            last_name=updated_user.last_name or "",
            company=updated_user.company or "",
            is_active=updated_user.is_active,
            balance=float(updated_user.balance),
            is_superuser=updated_user.is_superuser
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при обновлении профиля: {str(e)}"
        )