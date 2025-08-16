import asyncio
import aiohttp
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime
from src.account.models.wallet import Wallet, WalletDeposit

logger = logging.getLogger(__name__)


class AptosIntegrationService:
    """Сервис для интеграции с APTOS блокчейном"""
    
    def __init__(self, aptos_node_url: str = "https://fullnode.mainnet.aptoslabs.com"):
        self.aptos_node_url = aptos_node_url
        self.usdt_coin_type = "0x1::coin::CoinStore<0x1::aptos_coin::AptosCoin>"  # APTOS USDT
        
    async def get_wallet_balance(self, wallet_address: str) -> Dict[str, Any]:
        """Получает баланс кошелька в APTOS"""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.aptos_node_url}/v1/accounts/{wallet_address}/resource/{self.usdt_coin_type}"
                
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        balance = float(data.get('data', {}).get('coin', {}).get('value', 0))
                        
                        return {
                            "wallet_address": wallet_address,
                            "network": "APTOS",
                            "usdt_balance": balance,
                            "usd_equivalent": balance,
                            "last_updated": datetime.utcnow()
                        }
                    else:
                        logger.warning(f"Failed to get balance for {wallet_address}: {response.status}")
                        return {
                            "wallet_address": wallet_address,
                            "network": "APTOS",
                            "usdt_balance": 0.0,
                            "usd_equivalent": 0.0,
                            "last_updated": datetime.utcnow()
                        }
                        
        except Exception as e:
            logger.error(f"Error getting balance for {wallet_address}: {e}")
            return {
                "wallet_address": wallet_address,
                "network": "APTOS",
                "usdt_balance": 0.0,
                "usd_equivalent": 0.0,
                "last_updated": datetime.utcnow()
            }

    async def get_wallet_transactions(self, wallet_address: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Получает транзакции кошелька"""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.aptos_node_url}/v1/accounts/{wallet_address}/transactions"
                params = {"limit": limit}
                
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return self._parse_transactions(data, wallet_address)
                    else:
                        logger.warning(f"Failed to get transactions for {wallet_address}: {response.status}")
                        return []
                        
        except Exception as e:
            logger.error(f"Error getting transactions for {wallet_address}: {e}")
            return []

    def _parse_transactions(self, transactions_data: List[Dict], wallet_address: str) -> List[Dict[str, Any]]:
        """Парсит транзакции и фильтрует входящие USDT переводы"""
        parsed_transactions = []
        
        for tx in transactions_data:
            try:
                # Проверяем, что это входящая транзакция
                if self._is_incoming_transaction(tx, wallet_address):
                    # Проверяем, что это USDT перевод
                    if self._is_usdt_transfer(tx):
                        parsed_tx = self._parse_usdt_transfer(tx, wallet_address)
                        if parsed_tx:
                            parsed_transactions.append(parsed_tx)
                            
            except Exception as e:
                logger.error(f"Error parsing transaction {tx.get('hash', 'unknown')}: {e}")
                continue
                
        return parsed_transactions

    def _is_incoming_transaction(self, tx: Dict, wallet_address: str) -> bool:
        """Проверяет, является ли транзакция входящей для указанного кошелька"""
        # Проверяем, что кошелек является получателем
        if 'payload' in tx and 'function' in tx['payload']:
            function = tx['payload']['function']
            # Проверяем, что это функция перевода
            if 'transfer' in function.lower():
                # В APTOS нужно проверять аргументы транзакции
                # Это упрощенная проверка
                return True
        return False

    def _is_usdt_transfer(self, tx: Dict) -> bool:
        """Проверяет, является ли транзакция переводом USDT"""
        # Проверяем тип токена в транзакции
        if 'payload' in tx and 'type_arguments' in tx['payload']:
            type_args = tx['payload']['type_arguments']
            # Проверяем, что это USDT токен
            for arg in type_args:
                if 'usdt' in arg.lower() or 'aptos_coin' in arg.lower():
                    return True
        return False

    def _parse_usdt_transfer(self, tx: Dict, wallet_address: str) -> Optional[Dict[str, Any]]:
        """Парсит USDT перевод и возвращает структурированные данные"""
        try:
            tx_hash = tx.get('hash', '')
            amount = self._extract_transfer_amount(tx)
            block_number = tx.get('sequence_number', 0)
            
            if amount > 0:
                return {
                    "transaction_hash": tx_hash,
                    "amount": amount,
                    "usd_amount": amount,
                    "block_number": block_number,
                    "timestamp": tx.get('timestamp', datetime.utcnow().isoformat()),
                    "status": "pending"
                }
        except Exception as e:
            logger.error(f"Error parsing USDT transfer: {e}")
            
        return None

    def _extract_transfer_amount(self, tx: Dict) -> float:
        """Извлекает сумму перевода из транзакции"""
        try:
            # В APTOS сумма может быть в разных местах в зависимости от типа транзакции
            if 'events' in tx:
                for event in tx['events']:
                    if 'data' in event and 'amount' in event['data']:
                        return float(event['data']['amount'])
                        
            # Альтернативный способ - через payload
            if 'payload' in tx and 'arguments' in tx['payload']:
                args = tx['payload']['arguments']
                if len(args) >= 2:
                    try:
                        return float(args[1])
                    except (ValueError, TypeError):
                        pass
                        
        except Exception as e:
            logger.error(f"Error extracting transfer amount: {e}")
            
        return 0.0

    async def monitor_wallet_for_deposits(self, wallet: Wallet) -> List[Dict[str, Any]]:
        """Мониторит кошелек на предмет новых пополнений"""
        try:
            # Получаем последние транзакции
            transactions = await self.get_wallet_transactions(wallet.address, limit=50)
            
            # Фильтруем только новые транзакции (можно добавить проверку по времени)
            new_deposits = []
            for tx in transactions:
                # Здесь можно добавить логику для проверки, что транзакция новая
                # Например, сравнивать с последней обработанной транзакцией
                new_deposits.append(tx)
                
            return new_deposits
            
        except Exception as e:
            logger.error(f"Error monitoring wallet {wallet.address}: {e}")
            return []

    async def get_usdt_price(self) -> float:
        """Получает текущую цену USDT в USD"""
        try:
            return 1.0
        except Exception as e:
            logger.error(f"Error getting USDT price: {e}")
            return 1.0
