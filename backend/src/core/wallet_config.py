import os
from typing import Optional


class WalletConfig:
    """Конфигурация для системы кошельков"""
    
    # APTOS настройки
    APTOS_NODE_URL: str = os.getenv("APTOS_NODE_URL", "https://fullnode.mainnet.aptoslabs.com")
    APTOS_TESTNET_NODE_URL: str = os.getenv("APTOS_TESTNET_NODE_URL", "https://fullnode.testnet.aptoslabs.com")
    
    # Ключ шифрования для сид фраз (ОБЯЗАТЕЛЬНО установить в продакшене!)
    WALLET_ENCRYPTION_KEY: Optional[str] = os.getenv("WALLET_ENCRYPTION_KEY")
    
    # Настройки мониторинга
    WALLET_MONITORING_INTERVAL_MINUTES: int = int(os.getenv("WALLET_MONITORING_INTERVAL_MINUTES", "5"))
    WALLET_MONITORING_BATCH_SIZE: int = int(os.getenv("WALLET_MONITORING_BATCH_SIZE", "100"))
    
    # Настройки USDT
    USDT_CONTRACT_ADDRESS: str = os.getenv("USDT_CONTRACT_ADDRESS", "0x1::aptos_coin::AptosCoin")
    USDT_DECIMALS: int = int(os.getenv("USDT_DECIMALS", "8"))
    
    # Настройки безопасности
    MAX_WALLETS_PER_USER: int = int(os.getenv("MAX_WALLETS_PER_USER", "5"))
    WALLET_GENERATION_COOLDOWN_MINUTES: int = int(os.getenv("WALLET_GENERATION_COOLDOWN_MINUTES", "60"))
    
    # Настройки уведомлений
    ENABLE_DEPOSIT_NOTIFICATIONS: bool = os.getenv("ENABLE_DEPOSIT_NOTIFICATIONS", "true").lower() == "true"
    MIN_DEPOSIT_AMOUNT_USD: float = float(os.getenv("MIN_DEPOSIT_AMOUNT_USD", "1.0"))
    
    @classmethod
    def validate_config(cls) -> bool:
        """Проверяет корректность конфигурации"""
        if not cls.WALLET_ENCRYPTION_KEY:
            print("WARNING: WALLET_ENCRYPTION_KEY not set! Using generated key (NOT SAFE FOR PRODUCTION)")
            return False
        
        if cls.WALLET_MONITORING_INTERVAL_MINUTES < 1:
            print("ERROR: WALLET_MONITORING_INTERVAL_MINUTES must be at least 1")
            return False
            
        return True
    
    @classmethod
    def get_aptos_url(cls, use_testnet: bool = False) -> str:
        """Возвращает URL APTOS ноды"""
        return cls.APTOS_TESTNET_NODE_URL if use_testnet else cls.APTOS_NODE_URL
