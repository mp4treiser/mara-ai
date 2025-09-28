import os
import secrets
import hashlib
import asyncio
import logging
from typing import Optional, Tuple
from cryptography.fernet import Fernet
from src.account.repositories.wallet import WalletRepository
from src.account.models.wallet import Wallet, WalletDeposit
from src.account.repositories.user import UserRepository
from src.account.services.arbitrum_integration import ArbitrumIntegrationService
from src.account.services.wallet_generator import WalletGenerator

logger = logging.getLogger(__name__)


class WalletService:
    def __init__(self, db_session, encryption_key: Optional[str] = None):
        self.db = db_session
        self.wallet_repo = WalletRepository(db_session)
        self.user_repo = UserRepository(db_session)
        self.arbitrum_service = ArbitrumIntegrationService()
        self.wallet_generator = WalletGenerator()
        
        # Ключ шифрования для сид фраз (в продакшене должен храниться в безопасном месте)
        if encryption_key:
            self.fernet = Fernet(encryption_key)
        else:
            # Получаем ключ из переменных окружения
            import os
            env_key = os.getenv('WALLET_ENCRYPTION_KEY')
            if env_key:
                try:
                    self.fernet = Fernet(env_key.encode())
                    logger.info("Using encryption key from environment")
                except Exception as e:
                    logger.error(f"Invalid encryption key from environment: {e}")
                    # Fallback к фиксированному ключу
                    FIXED_ENCRYPTION_KEY = b'M74r9S6zybTwSO4F5rbnjgSc836bbN57YFi7xqJhy9Q='
                    self.fernet = Fernet(FIXED_ENCRYPTION_KEY)
            else:
                # Fallback к фиксированному ключу
                FIXED_ENCRYPTION_KEY = b'M74r9S6zybTwSO4F5rbnjgSc836bbN57YFi7xqJhy9Q='
                self.fernet = Fernet(FIXED_ENCRYPTION_KEY)
                logger.warning("Using fallback encryption key")

    async def generate_ethereum_wallet(self, user_id: int) -> Wallet:
        """Генерирует новый Ethereum кошелек для пользователя"""
        try:
            logger.info(f"Начинаем генерацию кошелька для пользователя {user_id}")
            
            # Генерируем криптографически стойкий кошелек
            wallet_data = self.wallet_generator.generate_wallet()
            
            # Шифруем мнемоническую фразу
            mnemonic_str = str(wallet_data["mnemonic"])
            encrypted_seed = self.fernet.encrypt(mnemonic_str.encode()).decode()
            
            # Создаем кошелек
            wallet = Wallet(
                user_id=user_id,
                address=wallet_data["address"],
                seed_phrase=encrypted_seed,
                network="ARBITRUM",
                is_active=True
            )
            
            logger.info(f"Кошелек успешно сгенерирован для пользователя {user_id}, адрес: {wallet_data['address']}")
            
            return await self.wallet_repo.create_wallet(wallet)
            
        except Exception as e:
            logger.error(f"Ошибка при генерации кошелька для пользователя {user_id}: {e}")

    async def get_user_wallet(self, user_id: int, network: str = "ARBITRUM") -> Optional[Wallet]:
        """Получить кошелек пользователя по сети"""
        return await self.wallet_repo.get_user_wallet_by_network(user_id, network)

    async def get_or_create_wallet(self, user_id: int, network: str = "ARBITRUM") -> Wallet:
        """Получить существующий кошелек или создать новый"""
        wallet = await self.get_user_wallet(user_id, network)
        if not wallet:
            wallet = await self.generate_ethereum_wallet(user_id)
        return wallet

    async def monitor_wallet_transactions(self, wallet: Wallet) -> list[WalletDeposit]:
        """Мониторит транзакции кошелька и возвращает новые пополнения"""
        try:
            # Используем Arbitrum интеграцию для мониторинга
            new_deposits_data = await self.arbitrum_service.monitor_wallet_for_deposits(wallet)
            
            new_deposits = []
            for deposit_data in new_deposits_data:
                # Проверяем, что такое пополнение еще не обрабатывалось
                existing_deposit = await self.wallet_repo.get_deposit_by_hash(deposit_data['transaction_hash'])
                if not existing_deposit:
                    # Создаем новую запись о пополнении USDT
                    deposit = WalletDeposit(
                        wallet_id=wallet.id,
                        transaction_hash=deposit_data['transaction_hash'],
                        amount=deposit_data['amount'],  # В USDT
                        usd_amount=deposit_data['amount'],  # USDT = USD
                        status='pending',  # Новые депозиты начинают как pending
                        block_number=deposit_data.get('block_number'),
                        from_address=deposit_data.get('from_address'),
                        to_address=deposit_data.get('to_address'),
                        gas_used=deposit_data.get('gas_used'),
                        gas_price=deposit_data.get('gas_price')
                    )
                    
                    # Сохраняем в БД
                    saved_deposit = await self.wallet_repo.create_deposit(deposit)
                    new_deposits.append(saved_deposit)
                    logger.info(f"Created new USDT deposit record: {deposit_data['transaction_hash']} - {deposit_data['amount']} USDT")
            
            # Обновляем время последней проверки
            await self.wallet_repo.update_wallet_last_checked(wallet.id)
            
            return new_deposits
            
        except Exception as e:
            print(f"Error monitoring wallet transactions: {e}")
            return []

    def monitor_wallet_transactions_sync(self, wallet: Wallet) -> list[WalletDeposit]:
        """Синхронная версия мониторинга транзакций для использования в Celery"""
        try:
            import requests
            import os
            
            # Получаем транзакции напрямую через API (синхронно)
            api_key = os.getenv('ARBITRUM_SCAN_API_KEY', 'JMK18R5B4R2DPPGMVFF9EXRMD5ISAJH63Z')
            api_url = f"https://api.etherscan.io/v2/api?chainid=42161&apikey={api_key}"
            
            params = {
                'module': 'account',
                'action': 'tokentx',
                'address': wallet.address,
                'startblock': 0,
                'endblock': 99999999,
                'page': 1,
                'offset': 50,
                'sort': 'desc'
            }
            
            logger.info(f"Getting transactions for wallet {wallet.address}")
            response = requests.get(api_url, params=params, timeout=30)
            
            if response.status_code != 200:
                logger.error(f"API request failed with status {response.status_code}")
                return []
            
            data = response.json()
            if data.get('status') != '1':
                logger.error(f"API returned error: {data.get('message', 'Unknown error')}")
                return []
            
            transactions = data.get('result', [])
            logger.info(f"Retrieved {len(transactions)} transactions for {wallet.address}")
            
            new_deposits = []
            usdt_transactions = 0
            
            for tx in transactions:
                # Проверяем, что это USDT транзакция
                if (tx.get('tokenName') == 'USD₮0' and 
                    tx.get('tokenSymbol') == 'USD₮0' and
                    tx.get('contractAddress', '').lower() == '0xfd086bc7cd5c481dcc9c85ebe478a1c0b69fcbb9'):
                    
                    usdt_transactions += 1
                    logger.info(f"Found USDT transaction #{usdt_transactions}")
                    
                    # Проверяем, что это входящая транзакция (to наш адрес)
                    if tx.get('to', '').lower() == wallet.address.lower():
                        logger.info(f"Transaction is TO our wallet: {wallet.address}")
                        
                        # Проверяем, что это не наша собственная транзакция
                        if tx.get('from', '').lower() != wallet.address.lower():
                            logger.info(f"Transaction is FROM external address: {tx.get('from', '')}")
                            
                            # Конвертируем amount из наименьших единиц USDT (6 знаков)
                            amount_wei = int(tx.get('value', 0))
                            amount_usdt = amount_wei / 10**6  # USDT имеет 6 знаков после запятой
                            
                            deposit_data = {
                                'transaction_hash': tx.get('hash', ''),
                                'from_address': tx.get('from', ''),
                                'to_address': tx.get('to', ''),
                                'amount': amount_usdt,  # В USDT, не в wei
                                'amount_wei': amount_wei,  # Оригинальное значение в wei
                                'block_number': int(tx.get('blockNumber', 0)),
                                'timestamp': int(tx.get('timeStamp', 0)),
                                'gas_used': int(tx.get('gasUsed', 0)),
                                'gas_price': int(tx.get('gasPrice', 0)),
                                'token_name': tx.get('tokenName', ''),
                                'token_symbol': tx.get('tokenSymbol', ''),
                                'contract_address': tx.get('contractAddress', ''),
                                'method_id': tx.get('methodId', ''),
                                'function_name': tx.get('functionName', '')
                            }
                            
                            # Проверяем, что такое пополнение еще не обрабатывалось
                            from src.core.orm.database import SessionLocal
                            from sqlalchemy import select
                            with SessionLocal() as sync_db:
                                existing_deposit = sync_db.execute(
                                    select(WalletDeposit).where(WalletDeposit.transaction_hash == deposit_data['transaction_hash'])
                                ).scalar_one_or_none()
                                
                                if not existing_deposit:
                                    # Создаем новую запись о пополнении USDT
                                    deposit = WalletDeposit(
                                        wallet_id=wallet.id,
                                        transaction_hash=deposit_data['transaction_hash'],
                                        amount=deposit_data['amount'],  # В USDT
                                        usd_amount=deposit_data['amount'],  # USDT = USD
                                        status='pending',  # Новые депозиты начинают как pending
                                        block_number=deposit_data.get('block_number')
                                    )
                                    
                                    # Сохраняем в БД
                                    sync_db.add(deposit)
                                    sync_db.commit()
                                    sync_db.refresh(deposit)
                                    
                                    new_deposits.append(deposit)
                                    logger.info(f"✅ Found new USDT deposit: {tx.get('hash', '')} - {amount_usdt} USDT")
                                else:
                                    logger.info(f"Deposit {deposit_data['transaction_hash']} already exists, skipping")
                        else:
                            logger.info(f"❌ Transaction is FROM our own wallet, skipping")
                    else:
                        logger.info(f"❌ Transaction is TO different address: {tx.get('to', '')}")
                else:
                    logger.info(f"❌ Not a USDT transaction")
            
            logger.info(f"Summary: {usdt_transactions} USDT transactions found, {len(new_deposits)} new deposits")
            
            # Обновляем время последней проверки
            from src.core.orm.database import SessionLocal
            from sqlalchemy import text
            from datetime import datetime
            with SessionLocal() as sync_db:
                sync_db.execute(
                    text("UPDATE wallets SET last_checked = :now WHERE id = :wallet_id"),
                    {"now": datetime.utcnow(), "wallet_id": wallet.id}
                )
                sync_db.commit()
            
            return new_deposits
            
        except Exception as e:
            logger.error(f"Error in sync wallet monitoring: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return []

    def process_deposit(self, deposit: WalletDeposit) -> bool:
        """Обрабатывает пополнение и пополняет баланс пользователя"""
        try:
            from src.core.orm.database import SessionLocal
            from sqlalchemy import select, text
            from src.account.models.wallet import Wallet
            from src.account.models.user import User
            from datetime import datetime
            
            with SessionLocal() as sync_db:
                # Получаем кошелек
                wallet = sync_db.execute(
                    select(Wallet).where(Wallet.id == deposit.wallet_id)
                ).scalar_one_or_none()
                if not wallet:
                    logger.error(f"Wallet {deposit.wallet_id} not found")
                    return False
                
                # Получаем пользователя
                user = sync_db.execute(
                    select(User).where(User.id == wallet.user_id)
                ).scalar_one_or_none()
                if not user:
                    logger.error(f"User {wallet.user_id} not found")
                    return False
                
                # Пополняем баланс пользователя
                new_balance = float(user.balance) + float(deposit.usd_amount)
                sync_db.execute(
                    text("UPDATE users SET balance = :balance WHERE id = :user_id"),
                    {"balance": new_balance, "user_id": wallet.user_id}
                )
                
                # Обновляем статус пополнения
                sync_db.execute(
                    text("UPDATE wallet_deposits SET status = :status, processed_at = :processed_at WHERE id = :deposit_id"),
                    {"status": "processed", "processed_at": datetime.utcnow(), "deposit_id": deposit.id}
                )
                
                sync_db.commit()
                logger.info(f"Successfully processed deposit {deposit.transaction_hash}: +{deposit.usd_amount} USD for user {wallet.user_id}")
                return True
                
        except Exception as e:
            logger.error(f"Error processing deposit: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
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
        # В реальности используйте Ethereum SDK для генерации адреса
        # Пока генерируем случайный хеш
        seed_hash = hashlib.sha256(seed_phrase.encode()).hexdigest()
        return f"0x{seed_hash[:40]}"  # Ethereum адреса начинаются с 0x и имеют длину 40 символов

    def decrypt_seed_phrase(self, encrypted_seed: str) -> str:
        """Расшифровывает сид фразу (только для админов)"""
        try:
            decrypted = self.fernet.decrypt(encrypted_seed.encode())
            return decrypted.decode()
        except Exception as e:
            logger.error(f"Error decrypting seed phrase: {e}")
            return ""
    
    def hash_seed_phrase(self, mnemonic_phrase: str) -> str:
        """
        Хэширует мнемоническую фразу для админов
        
        Args:
            mnemonic_phrase: Мнемоническая фраза (12 слов через пробел)
            
        Returns:
            Зашифрованная мнемоническая фраза
        """
        try:
            # Шифруем мнемоническую фразу тем же способом, что и в generate_ethereum_wallet
            encrypted_seed = self.fernet.encrypt(mnemonic_phrase.encode()).decode()
            return encrypted_seed
        except Exception as e:
            logger.error(f"Error hashing seed phrase: {e}")
            return ""
    
    async def get_wallet_mnemonic(self, wallet: Wallet) -> str:
        """Получает мнемоническую фразу кошелька (только для владельца)"""
        try:
            return self.decrypt_seed_phrase(wallet.seed_phrase)
        except Exception as e:
            logger.error(f"Ошибка при получении мнемонической фразы: {e}")
            return ""

    async def get_wallet_balance(self, wallet: Wallet) -> dict:
        """Получает баланс кошелька (интеграция с Ethereum API)"""
        try:
            # Используем Ethereum интеграцию для получения баланса
            balance_info = await self.arbitrum_service.get_wallet_balance(wallet.address)
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
