from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import and_, select
from src.account.models.wallet import Wallet, WalletDeposit


class WalletRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_wallet(self, wallet: Wallet) -> Wallet:
        """Создать новый кошелек"""
        self.db.add(wallet)
        await self.db.commit()
        await self.db.refresh(wallet)
        return wallet

    async def get_wallet_by_id(self, wallet_id: int) -> Optional[Wallet]:
        """Получить кошелек по ID"""
        result = await self.db.execute(select(Wallet).where(Wallet.id == wallet_id))
        return result.scalar_one_or_none()

    async def get_wallet_by_address(self, address: str) -> Optional[Wallet]:
        """Получить кошелек по адресу"""
        result = await self.db.execute(select(Wallet).where(Wallet.address == address))
        return result.scalar_one_or_none()

    async def get_user_wallets(self, user_id: int) -> List[Wallet]:
        """Получить все кошельки пользователя"""
        result = await self.db.execute(
            select(Wallet).where(
                and_(Wallet.user_id == user_id, Wallet.is_active == True)
            )
        )
        return result.scalars().all()

    async def get_user_wallet_by_network(self, user_id: int, network: str) -> Optional[Wallet]:
        """Получить кошелек пользователя по сети"""
        result = await self.db.execute(
            select(Wallet).where(
                and_(
                    Wallet.user_id == user_id,
                    Wallet.network == network,
                    Wallet.is_active == True
                )
            )
        )
        return result.scalar_one_or_none()

    async def update_wallet_last_checked(self, wallet_id: int) -> None:
        """Обновить время последней проверки кошелька"""
        from datetime import datetime
        stmt = select(Wallet).where(Wallet.id == wallet_id)
        result = await self.db.execute(stmt)
        wallet = result.scalar_one_or_none()
        if wallet:
            wallet.last_checked = datetime.utcnow()
            await self.db.commit()

    async def create_deposit(self, deposit: WalletDeposit) -> WalletDeposit:
        """Создать запись о пополнении"""
        self.db.add(deposit)
        await self.db.commit()
        await self.db.refresh(deposit)
        return deposit

    async def get_deposits_by_wallet(self, wallet_id: int) -> List[WalletDeposit]:
        """Получить все пополнения кошелька"""
        result = await self.db.execute(
            select(WalletDeposit).where(WalletDeposit.wallet_id == wallet_id)
        )
        return result.scalars().all()

    async def get_deposit_by_hash(self, transaction_hash: str) -> Optional[WalletDeposit]:
        """Получить пополнение по хешу транзакции"""
        result = await self.db.execute(
            select(WalletDeposit).where(WalletDeposit.transaction_hash == transaction_hash)
        )
        return result.scalar_one_or_none()

    async def get_deposit_by_id(self, deposit_id: int) -> Optional[WalletDeposit]:
        """Получить пополнение по ID"""
        result = await self.db.execute(
            select(WalletDeposit).where(WalletDeposit.id == deposit_id)
        )
        return result.scalar_one_or_none()

    async def get_pending_deposits(self) -> List[WalletDeposit]:
        """Получить все ожидающие обработки пополнения"""
        result = await self.db.execute(
            select(WalletDeposit).where(WalletDeposit.status == "pending")
        )
        return result.scalars().all()

    async def update_deposit_status(self, deposit_id: int, status: str) -> None:
        """Обновить статус пополнения"""
        from datetime import datetime
        stmt = select(WalletDeposit).where(WalletDeposit.id == deposit_id)
        deposit = await self.db.execute(stmt)
        deposit = deposit.scalar_one_or_none()
        if deposit:
            deposit.status = status
            if status == "processed":
                deposit.processed_at = datetime.utcnow()
            await self.db.commit()

    async def get_wallets_for_monitoring(self, limit: int = 100) -> List[Wallet]:
        """Получить кошельки для мониторинга (активные и недавно не проверенные)"""
        from datetime import datetime, timedelta
        cutoff_time = datetime.utcnow() - timedelta(minutes=5)  # Проверяем каждые 5 минут
        
        result = await self.db.execute(
            select(Wallet).where(
                and_(
                    Wallet.is_active == True,
                    (Wallet.last_checked.is_(None) | (Wallet.last_checked < cutoff_time))
                )
            ).limit(limit)
        )
        return result.scalars().all()
