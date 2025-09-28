import logging
from typing import Dict
from bip_utils import Bip39MnemonicGenerator, Bip39SeedGenerator, Bip44, Bip44Coins, Bip44Changes
import traceback

logger = logging.getLogger(__name__)


class WalletGenerator:
    """
    Класс для генерации Ethereum кошельков совместимых с MetaMask
    """
    
    def __init__(self):
        pass

    def generate_wallet(self, strength: int = 128, passphrase: str = "") -> Dict[str, str]:
        """
        Генерирует полный Ethereum кошелек.

        Args:
            strength: Количество бит энтропии.
            passphrase: Дополнительная парольная фраза.

        Returns:
            Словарь с данными кошелька.
        """
        try:
            # Генерируем мнемоническую фразу
            mnemonic = Bip39MnemonicGenerator().FromWordsNumber(12)
            
            # Преобразуем в seed
            seed_bytes = Bip39SeedGenerator(mnemonic).Generate(passphrase)
            
            # Используем BIP44 для Ethereum
            bip44_mst = Bip44.FromSeed(seed_bytes, Bip44Coins.ETHEREUM)
            bip44_acc = bip44_mst.Purpose().Coin().Account(0).Change(Bip44Changes.CHAIN_EXT).AddressIndex(0)
            
            # Получаем адрес и приватный ключ
            address = bip44_acc.PublicKey().ToAddress()
            private_key = bip44_acc.PrivateKey().Raw().ToHex()

            return {
                "mnemonic": mnemonic,
                "address": address,
                "private_key": private_key,
                "seed": seed_bytes.hex(),
                "network": "ARBITRUM"
            }
        except Exception as e:
            logger.error(f"Ошибка при генерации кошелька: {e}")
            logger.error(f"Traceback: {traceback.format_exc()}")
