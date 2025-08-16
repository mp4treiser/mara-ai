import os
import secrets
import hashlib
import asyncio
from typing import Optional, Tuple
from cryptography.fernet import Fernet
from src.account.repositories.wallet import WalletRepository
from src.account.models.wallet import Wallet, WalletDeposit
from src.account.repositories.user import UserRepository
from src.account.services.aptos_integration import AptosIntegrationService


class WalletService:
    def __init__(self, db_session, encryption_key: Optional[str] = None):
        self.db = db_session
        self.wallet_repo = WalletRepository(db_session)
        self.user_repo = UserRepository(db_session)
        self.aptos_service = AptosIntegrationService()
        
        # Ключ шифрования для сид фраз (в продакшене должен храниться в безопасном месте)
        if encryption_key:
            self.fernet = Fernet(encryption_key)
        else:
            # Генерируем ключ если не передан (только для разработки!)
            key = Fernet.generate_key()
            self.fernet = Fernet(key)
            print(f"WARNING: Generated new encryption key: {key.decode()}")

    def generate_aptos_wallet(self, user_id: int) -> Wallet:
        """Генерирует новый APTOS кошелек для пользователя"""
        # Генерируем случайную сид фразу (в реальности используйте более надежные методы)
        seed_phrase = self._generate_seed_phrase()
        
        # Генерируем адрес кошелька (упрощенная версия)
        wallet_address = self._generate_wallet_address(seed_phrase)
        
        # Шифруем сид фразу
        encrypted_seed = self.fernet.encrypt(seed_phrase.encode()).decode()
        
        # Создаем кошелек
        wallet = Wallet(
            user_id=user_id,
            address=wallet_address,
            seed_phrase=encrypted_seed,
            network="APTOS",
            is_active=True
        )
        
        return self.wallet_repo.create_wallet(wallet)

    def get_user_wallet(self, user_id: int, network: str = "APTOS") -> Optional[Wallet]:
        """Получить кошелек пользователя по сети"""
        return self.wallet_repo.get_user_wallet_by_network(user_id, network)

    def get_or_create_wallet(self, user_id: int, network: str = "APTOS") -> Wallet:
        """Получить существующий кошелек или создать новый"""
        wallet = self.get_user_wallet(user_id, network)
        if not wallet:
            wallet = self.generate_aptos_wallet(user_id)
        return wallet

    async def monitor_wallet_transactions(self, wallet: Wallet) -> list[WalletDeposit]:
        """Мониторит транзакции кошелька и возвращает новые пополнения"""
        try:
            # Используем APTOS интеграцию для мониторинга
            new_deposits_data = await self.aptos_service.monitor_wallet_for_deposits(wallet)
            
            new_deposits = []
            for deposit_data in new_deposits_data:
                # Проверяем, что такое пополнение еще не обрабатывалось
                existing_deposit = self.wallet_repo.get_deposit_by_hash(deposit_data['transaction_hash'])
                if not existing_deposit:
                    # Создаем новую запись о пополнении
                    deposit = WalletDeposit(
                        wallet_id=wallet.id,
                        transaction_hash=deposit_data['transaction_hash'],
                        amount=deposit_data['amount'],
                        usd_amount=deposit_data['usd_amount'],
                        status=deposit_data['status'],
                        block_number=deposit_data.get('block_number')
                    )
                    new_deposits.append(deposit)
            
            # Обновляем время последней проверки
            self.wallet_repo.update_wallet_last_checked(wallet.id)
            
            return new_deposits
            
        except Exception as e:
            print(f"Error monitoring wallet transactions: {e}")
            return []

    def monitor_wallet_transactions_sync(self, wallet: Wallet) -> list[WalletDeposit]:
        """Синхронная версия мониторинга транзакций для использования в Celery"""
        try:
            # Запускаем асинхронную функцию в event loop
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                new_deposits = loop.run_until_complete(self.monitor_wallet_transactions(wallet))
                return new_deposits
            finally:
                loop.close()
        except Exception as e:
            print(f"Error in sync wallet monitoring: {e}")
            return []

    def process_deposit(self, deposit: WalletDeposit) -> bool:
        """Обрабатывает пополнение и пополняет баланс пользователя"""
        try:
            # Получаем кошелек
            wallet = self.wallet_repo.get_wallet_by_id(deposit.wallet_id)
            if not wallet:
                return False
            
            # Получаем пользователя
            user = self.user_repo.get_user_by_id(wallet.user_id)
            if not user:
                return False
            
            # Пополняем баланс пользователя
            new_balance = float(user.balance) + deposit.usd_amount
            self.user_repo.update_user_balance(wallet.user_id, new_balance)
            
            # Обновляем статус пополнения
            self.wallet_repo.update_deposit_status(deposit.id, "processed")
            
            return True
        except Exception as e:
            print(f"Error processing deposit: {e}")
            return False

    def _generate_seed_phrase(self) -> str:
        """Генерирует случайную сид фразу (упрощенная версия)"""
        # В реальности используйте BIP39 или аналогичные стандарты
        words = [
            "abandon", "ability", "able", "about", "above", "absent", "absorb", "abstract",
            "absurd", "abuse", "access", "accident", "account", "accuse", "achieve", "acid"
        ]
        return " ".join(secrets.choice(words) for _ in range(12))

    def _generate_wallet_address(self, seed_phrase: str) -> str:
        """Генерирует адрес кошелька на основе сид фразы"""
        # В реальности используйте APTOS SDK для генерации адреса
        # Пока генерируем случайный хеш
        seed_hash = hashlib.sha256(seed_phrase.encode()).hexdigest()
        return f"0x{seed_hash[:40]}"  # APTOS адреса начинаются с 0x и имеют длину 64 символа

    def decrypt_seed_phrase(self, encrypted_seed: str) -> str:
        """Расшифровывает сид фразу (только для админов)"""
        try:
            decrypted = self.fernet.decrypt(encrypted_seed.encode())
            return decrypted.decode()
        except Exception as e:
            print(f"Error decrypting seed phrase: {e}")
            return ""

    async def get_wallet_balance(self, wallet: Wallet) -> dict:
        """Получает баланс кошелька (интеграция с APTOS API)"""
        try:
            # Используем APTOS интеграцию для получения баланса
            balance_info = await self.aptos_service.get_wallet_balance(wallet.address)
            return balance_info
        except Exception as e:
            print(f"Error getting wallet balance: {e}")
            # Возвращаем заглушку в случае ошибки
            return {
                "wallet_address": wallet.address,
                "network": wallet.network,
                "usdt_balance": 0.0,
                "usd_equivalent": 0.0,
                "last_updated": wallet.last_checked or wallet.created_at
            }

    def get_wallet_balance_sync(self, wallet: Wallet) -> dict:
        """Синхронная версия получения баланса кошелька"""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                balance_info = loop.run_until_complete(self.get_wallet_balance(wallet))
                return balance_info
            finally:
                loop.close()
        except Exception as e:
            print(f"Error in sync balance getting: {e}")
            return {
                "wallet_address": wallet.address,
                "network": wallet.network,
                "usdt_balance": 0.0,
                "usd_equivalent": 0.0,
                "last_updated": wallet.last_checked or wallet.created_at
            }
