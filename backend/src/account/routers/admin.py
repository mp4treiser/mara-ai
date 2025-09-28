from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.account.schemas import CreateUserSchema, UpdateUserSchema, BaseUserSchema
from src.account.services import UserService
from src.core.orm.database import get_async_session
from src.core.dependencies import get_current_user, get_current_active_user, get_current_superuser
from src.account.models.user import User
from src.account.models.wallet import Wallet
from src.account.repositories.wallet import WalletRepository

router = APIRouter(
    prefix="/admin/users",
    tags=["Admin"]
)


@router.get("/health")
async def health_handler():
    return {"detail": "success"}


@router.get("/", response_model=List[BaseUserSchema])
async def get_users_handler(
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_superuser)
):
    """Получить всех пользователей (только для суперпользователей)"""
    user_service = UserService(session=session)
    return await user_service.get_all()


@router.get("/{user_id}", response_model=BaseUserSchema)
async def get_user_by_id_handler(
    user_id: int, 
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_superuser)
):
    """Получить пользователя по ID (только для суперпользователей)"""
    user_service = UserService(session=session)
    return await user_service.get_by_id(user_id=user_id)


@router.post("/", response_model=BaseUserSchema)
async def create_user_handler(
    payload: CreateUserSchema, 
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_superuser)
):
    """Создать нового пользователя (только для суперпользователей)"""
    user_service = UserService(session=session)
    return await user_service.create(user_schema=payload)


@router.put("/{user_id}", response_model=BaseUserSchema)
async def update_user_handler(
    user_id: int, 
    payload: UpdateUserSchema,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_superuser)
):
    """Обновить пользователя (только для суперпользователей)"""
    user_service = UserService(session=session)
    return await user_service.update(user_id=user_id, user_schema=payload)


@router.delete("/{user_id}", response_model=None)
async def delete_user_handler(
    user_id: int, 
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_superuser)
):
    """Удалить пользователя (только для суперпользователей)"""
    user_service = UserService(session=session)
    return await user_service.delete(user_id=user_id)


@router.patch("/{user_id}/toggle-superuser", response_model=BaseUserSchema)
async def toggle_superuser_handler(
    user_id: int,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_superuser)
):
    """Переключить статус суперпользователя (только для суперпользователей)"""
    user_service = UserService(session=session)
    user = await user_service.get_by_id(user_id=user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found"
        )
    
    # Обновляем статус суперпользователя
    update_data = UpdateUserSchema(is_superuser=not user.is_superuser)
    return await user_service.update(user_id=user_id, user_schema=update_data)


@router.get("/{user_id}/wallets")
async def get_user_wallets_with_seeds_handler(
    user_id: int,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_superuser)
):
    """Получить кошельки пользователя с захешированными сид фразами (только для суперпользователей)"""
    wallet_repo = WalletRepository(session)
    wallets = await wallet_repo.get_user_wallets(user_id)
    
    wallet_data = []
    for wallet in wallets:
        wallet_data.append({
            "id": wallet.id,
            "address": wallet.address,
            "seed_phrase": wallet.seed_phrase,  # Захешированная сид фраза
            "network": wallet.network,
            "is_active": wallet.is_active,
            "created_at": wallet.created_at,
            "last_checked": wallet.last_checked
        })
    
    return {
        "user_id": user_id,
        "wallets": wallet_data
    }


@router.get("/wallets/all")
async def get_all_wallets_with_seeds_handler(
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_superuser)
):
    """Получить все кошельки с захешированными сид фразами (только для суперпользователей)"""
    wallet_repo = WalletRepository(session)
    
    # Получаем все кошельки с информацией о пользователях
    from sqlalchemy import select
    query = select(Wallet, User.email).join(User, Wallet.user_id == User.id)
    results = await session.execute(query)
    
    wallet_data = []
    for wallet, user_email in results:
        wallet_data.append({
            "id": wallet.id,
            "user_id": wallet.user_id,
            "user_email": user_email,
            "address": wallet.address,
            "seed_phrase": wallet.seed_phrase,  # Захешированная сид фраза
            "network": wallet.network,
            "is_active": wallet.is_active,
            "created_at": wallet.created_at,
            "last_checked": wallet.last_checked
        })
    
    return {
        "total_wallets": len(wallet_data),
        "wallets": wallet_data
    }