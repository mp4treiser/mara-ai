from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from src.core.orm.database import get_db
from src.core.dependencies import get_current_user
from src.account.schemas.wallet import WalletResponse, WalletCreate, WalletBalanceResponse
from src.account.services.wallet import WalletService
from src.account.models.user import User

router = APIRouter(prefix="/wallets", tags=["wallets"])


@router.post("/generate", response_model=WalletResponse)
async def generate_wallet(
    wallet_data: WalletCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Генерирует новый кошелек для текущего пользователя"""
    try:
        wallet_service = WalletService(db)
        wallet = wallet_service.get_or_create_wallet(
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
    db: Session = Depends(get_db)
):
    """Получить все кошельки текущего пользователя"""
    try:
        wallet_service = WalletService(db)
        wallets = wallet_service.wallet_repo.get_user_wallets(current_user.id)
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
    db: Session = Depends(get_db)
):
    """Получить кошелек пользователя по сети"""
    try:
        wallet_service = WalletService(db)
        wallet = wallet_service.get_user_wallet(current_user.id, network)
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
    db: Session = Depends(get_db)
):
    """Получить баланс кошелька пользователя"""
    try:
        wallet_service = WalletService(db)
        wallet = wallet_service.get_user_wallet(current_user.id, network)
        if not wallet:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Wallet for network {network} not found"
            )
        
        # Используем синхронную версию для получения баланса
        balance_info = wallet_service.get_wallet_balance_sync(wallet)
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
    db: Session = Depends(get_db)
):
    """Получить все кошельки (только для админов)"""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    try:
        wallet_service = WalletService(db)
        # Здесь можно добавить пагинацию
        wallets = db.query(wallet_service.wallet_repo.model).all()
        return wallets
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting all wallets: {str(e)}"
        )
