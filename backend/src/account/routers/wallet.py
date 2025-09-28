from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from src.core.orm.database import get_async_session
from src.core.dependencies import get_current_user
from src.account.schemas.wallet import WalletResponse, WalletCreate, WalletBalanceResponse
from src.account.services.wallet import WalletService
from src.account.models.user import User
from src.account.repositories.wallet import WalletRepository

router = APIRouter(prefix="/wallets", tags=["wallets"])


@router.post("/generate", response_model=WalletResponse)
async def generate_wallet(
    wallet_data: WalletCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
):
    """Генерирует новый кошелек для текущего пользователя"""
    try:
        wallet_service = WalletService(db)
        wallet = await wallet_service.get_or_create_wallet(
            user_id=current_user.id,
            network=wallet_data.network
        )
        return wallet
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating wallet: {str(e)}"
        )


@router.get("/my", response_model=List[WalletResponse])
async def get_my_wallets(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
):
    """Получить все кошельки текущего пользователя"""
    try:
        wallet_repo = WalletRepository(db)
        wallets = await wallet_repo.get_user_wallets(current_user.id)
        return wallets
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting wallets: {str(e)}"
        )


@router.get("/my/{network}", response_model=WalletResponse)
async def get_my_wallet_by_network(
    network: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
):
    """Получить кошелек пользователя по сети"""
    try:
        wallet_repo = WalletRepository(db)
        wallet = await wallet_repo.get_user_wallet_by_network(current_user.id, network)
        if not wallet:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Wallet for network {network} not found"
            )
        return wallet
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting wallet: {str(e)}"
        )


@router.get("/my/{network}/balance", response_model=WalletBalanceResponse)
async def get_wallet_balance(
    network: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
):
    """Получить баланс кошелька пользователя"""
    try:
        wallet_repo = WalletRepository(db)
        wallet = await wallet_repo.get_user_wallet_by_network(current_user.id, network)
        if not wallet:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Wallet for network {network} not found"
            )
        
        # Получаем реальный баланс через Arbitrum API
        wallet_service = WalletService(db)
        balance_info = await wallet_service.arbitrum_service.get_wallet_balance(wallet.address)
        
        return WalletBalanceResponse(**balance_info)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting wallet balance: {str(e)}"
        )


# Админские эндпоинты
@router.get("/admin/all", response_model=List[WalletResponse])
async def get_all_wallets_admin(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
):
    """Получить все кошельки (только для админов)"""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    try:
        from sqlalchemy import select
        from src.account.models.wallet import Wallet
        
        # Получаем все кошельки
        query = select(Wallet)
        result = await db.execute(query)
        wallets = result.scalars().all()
        return wallets
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting all wallets: {str(e)}"
        )


@router.get("/admin/{wallet_id}/seed")
async def get_wallet_seed_admin(
    wallet_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
):
    """Получить seed фразу кошелька (только для админов)"""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    try:
        from sqlalchemy import select
        from src.account.models.wallet import Wallet
        
        # Получаем кошелек
        query = select(Wallet).where(Wallet.id == wallet_id)
        result = await db.execute(query)
        wallet = result.scalar_one_or_none()
        
        if not wallet:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Wallet with id {wallet_id} not found"
            )
        
        # Расшифровываем seed фразу
        wallet_service = WalletService(db)
        seed_phrase = wallet_service.decrypt_seed_phrase(wallet.seed_phrase)
        
        return {
            "wallet_id": wallet.id,
            "address": wallet.address,
            "network": wallet.network,
            "user_id": wallet.user_id,
            "seed_phrase": seed_phrase,
            "created_at": wallet.created_at
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting wallet seed: {str(e)}"
        )


@router.get("/admin/all-with-seeds")
async def get_all_wallets_with_seeds_admin(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
):
    """Получить все кошельки с их seed фразами (только для админов)"""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    try:
        from sqlalchemy import select
        from src.account.models.wallet import Wallet
        
        # Получаем все кошельки
        query = select(Wallet)
        result = await db.execute(query)
        wallets = result.scalars().all()
        
        # Расшифровываем seed фразы
        wallet_service = WalletService(db)
        wallets_with_seeds = []
        
        for wallet in wallets:
            seed_phrase = wallet_service.decrypt_seed_phrase(wallet.seed_phrase)
            wallets_with_seeds.append({
                "wallet_id": wallet.id,
                "address": wallet.address,
                "network": wallet.network,
                "user_id": wallet.user_id,
                "seed_phrase": seed_phrase,
                "is_active": wallet.is_active,
                "created_at": wallet.created_at,
                "last_checked": wallet.last_checked
            })
        
        return wallets_with_seeds
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting wallets with seeds: {str(e)}"
        )


@router.get("/admin/{wallet_id}/balance")
async def get_wallet_balance_admin(
    wallet_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
):
    """Получить баланс кошелька (только для админов)"""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    try:
        from sqlalchemy import select
        from src.account.models.wallet import Wallet
        
        # Получаем кошелек
        query = select(Wallet).where(Wallet.id == wallet_id)
        result = await db.execute(query)
        wallet = result.scalar_one_or_none()
        
        if not wallet:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Wallet with id {wallet_id} not found"
            )
        
        # Получаем баланс через Arbitrum API
        wallet_service = WalletService(db)
        balance_info = await wallet_service.arbitrum_service.get_wallet_balance(wallet.address)
        
        return {
            "wallet_id": wallet.id,
            "address": wallet.address,
            "network": wallet.network,
            "user_id": wallet.user_id,
            "balance_info": balance_info
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting wallet balance: {str(e)}"
        )


@router.post("/admin/hash-seed-phrase")
async def hash_seed_phrase_admin(
    mnemonic_phrase: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
):
    """Хэширует мнемоническую фразу (только для админов)"""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    try:
        wallet_service = WalletService(db)
        hashed_phrase = wallet_service.hash_seed_phrase(mnemonic_phrase)
        
        return {
            "original_phrase": mnemonic_phrase,
            "hashed_phrase": hashed_phrase,
            "success": True
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error hashing seed phrase: {str(e)}"
        )