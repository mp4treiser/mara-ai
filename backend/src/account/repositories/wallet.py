from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_
from src.account.models.wallet import Wallet, WalletDeposit


class WalletRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_wallet(self, wallet: Wallet) -> Wallet:
        """Создать новый кошелек"""
        self.db.add(wallet)
        self.db.commit()
        self.db.refresh(wallet)
        return wallet

    def get_wallet_by_id(self, wallet_id: int) -> Optional[Wallet]:
        """Получить кошелек по ID"""
        return self.db.query(Wallet).filter(Wallet.id == wallet_id).first()

    def get_wallet_by_address(self, address: str) -> Optional[Wallet]:
        """Получить кошелек по адресу"""
        return self.db.query(Wallet).filter(Wallet.address == address).first()

    def get_user_wallets(self, user_id: int) -> List[Wallet]:
        """Получить все кошельки пользователя"""
        return self.db.query(Wallet).filter(
            and_(Wallet.user_id == user_id, Wallet.is_active == True)
        ).all()

    def get_user_wallet_by_network(self, user_id: int, network: str) -> Optional[Wallet]:
        """Получить кошелек пользователя по сети"""
        return self.db.query(Wallet).filter(
            and_(
                Wallet.user_id == user_id,
                Wallet.network == network,
                Wallet.is_active == True
            )
        ).first()

    def update_wallet_last_checked(self, wallet_id: int) -> None:
        """Обновить время последней проверки кошелька"""
        from datetime import datetime
        self.db.query(Wallet).filter(Wallet.id == wallet_id).update({
            "last_checked": datetime.utcnow()
        })
        self.db.commit()

    def create_deposit(self, deposit: WalletDeposit) -> WalletDeposit:
        """Создать запись о пополнении"""
        self.db.add(deposit)
        self.db.commit()
        self.db.refresh(deposit)
        return deposit

    def get_deposit_by_hash(self, transaction_hash: str) -> Optional[WalletDeposit]:
        """Получить пополнение по хешу транзакции"""
        return self.db.query(WalletDeposit).filter(
            WalletDeposit.transaction_hash == transaction_hash
        ).first()

    def get_deposit_by_id(self, deposit_id: int) -> Optional[WalletDeposit]:
        """Получить пополнение по ID"""
        return self.db.query(WalletDeposit).filter(
            WalletDeposit.id == deposit_id
        ).first()

    def get_pending_deposits(self) -> List[WalletDeposit]:
        """Получить все ожидающие обработки пополнения"""
        return self.db.query(WalletDeposit).filter(
            WalletDeposit.status == "pending"
        ).all()

    def update_deposit_status(self, deposit_id: int, status: str) -> None:
        """Обновить статус пополнения"""
        from datetime import datetime
        update_data = {"status": status}
        if status == "processed":
            update_data["processed_at"] = datetime.utcnow()
        
        self.db.query(WalletDeposit).filter(
            WalletDeposit.id == deposit_id
        ).update(update_data)
        self.db.commit()

    def get_wallets_for_monitoring(self, limit: int = 100) -> List[Wallet]:
        """Получить кошельки для мониторинга (активные и недавно не проверенные)"""
        from datetime import datetime, timedelta
        cutoff_time = datetime.utcnow() - timedelta(minutes=5)  # Проверяем каждые 5 минут
        
        return self.db.query(Wallet).filter(
            and_(
                Wallet.is_active == True,
                (Wallet.last_checked.is_(None) | (Wallet.last_checked < cutoff_time))
            )
        ).limit(limit).all()
