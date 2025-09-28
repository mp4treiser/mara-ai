import asyncio
import aiohttp
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime
from src.account.models.wallet import Wallet, WalletDeposit

logger = logging.getLogger(__name__)


class EthereumIntegrationService:
    """Сервис для интеграции с Ethereum блокчейном"""
    
    def __init__(self, ethereum_rpc_url: str = "https://eth-mainnet.g.alchemy.com/v2/-2MBzOTlVXIlZDC71fCHQIa4-44UKVsN"):
        self.ethereum_rpc_url = ethereum_rpc_url
        
    async def get_wallet_balance(self, wallet_address: str) -> Dict[str, Any]:
        """Получает баланс кошелька в Ethereum"""
        try:
            async with aiohttp.ClientSession() as session:
                # Получаем баланс ETH
                eth_balance = await self._get_eth_balance(session, wallet_address)
                
                # Получаем баланс USDT (ERC-20 токен)
                usdt_balance = await self._get_usdt_balance(session, wallet_address)
                
                # Получаем курс ETH к USD
                eth_usd_rate = await self._get_eth_usd_rate(session)
                
                # Рассчитываем общий USD эквивалент
                usd_equivalent = (eth_balance * eth_usd_rate) + usdt_balance
                
                return {
                    "wallet_address": wallet_address,
                    "network": "ETHEREUM",
                    "eth_balance": eth_balance,
                    "usdt_balance": usdt_balance,
                    "usd_equivalent": usd_equivalent,
                    "last_updated": datetime.utcnow()
                }
                        
        except Exception as e:
            logger.error(f"Error getting balance for {wallet_address}: {e}")
            return {
                "wallet_address": wallet_address,
                "network": "ETHEREUM",
                "eth_balance": 0.0,
                "usdt_balance": 0.0,
                "usd_equivalent": 0.0,
                "last_updated": datetime.utcnow()
            }
    
    async def _get_eth_balance(self, session: aiohttp.ClientSession, wallet_address: str) -> float:
        """Получает баланс ETH"""
        try:
            payload = {
                "jsonrpc": "2.0",
                "method": "eth_getBalance",
                "params": [wallet_address, "latest"],
                "id": 1
            }
            
            async with session.post(self.ethereum_rpc_url, json=payload) as response:
                print("xyu")
                print(response.json)
                if response.status == 200:
                    data = await response.json()
                    print(data)
                    if "result" in data:
                        # Конвертируем из wei в ETH
                        wei_balance = int(data["result"], 16)
                        print(wei_balance)
                        eth_balance = wei_balance / 10**18
                        print(eth_balance)
                        return eth_balance
                
                return 0.0
                
        except Exception as e:
            logger.error(f"Error getting ETH balance: {e}")
            return 0.0
    
    async def _get_usdt_balance(self, session: aiohttp.ClientSession, wallet_address: str) -> float:
        """Получает баланс USDT (ERC-20 токен)"""
        try:
            # USDT контракт на Ethereum mainnet
            usdt_contract = "0xdAC17F958D2ee523a2206206994597C13D831ec7"
            
            # Вызываем balanceOf функцию
            payload = {
                "jsonrpc": "2.0",
                "method": "eth_call",
                "params": [{
                    "to": usdt_contract,
                    "data": f"0x70a08231000000000000000000000000{wallet_address[2:].lower()}"
                }, "latest"],
                "id": 1
            }
            
            async with session.post(self.ethereum_rpc_url, json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    if "result" in data and data["result"] != "0x":
                        # Конвертируем из наименьших единиц USDT (6 знаков после запятой)
                        balance_hex = data["result"]
                        balance_int = int(balance_hex, 16)
                        usdt_balance = balance_int / 10**6
                        print(usdt_balance)
                        return usdt_balance
                
                return 0.0
                
        except Exception as e:
            logger.error(f"Error getting USDT balance: {e}")
            return 0.0
    
    async def monitor_wallet_for_deposits(self, wallet: Wallet) -> List[Dict[str, Any]]:
        """Мониторит кошелек на предмет новых депозитов"""
        try:
            # В реальной реализации здесь должен быть мониторинг блокчейна
            # Пока возвращаем пустой список
            logger.info(f"Monitoring wallet {wallet.address} for deposits")
            return []
            
        except Exception as e:
            logger.error(f"Error monitoring wallet {wallet.address}: {e}")
            return []
    
    async def _get_eth_usd_rate(self, session: aiohttp.ClientSession) -> float:
        """Получает курс ETH к USD"""
        try:
            # Используем CoinGecko API для получения курса
            url = "https://api.coingecko.com/api/v3/simple/price?ids=ethereum&vs_currencies=usd"
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    return data["ethereum"]["usd"]
                else:
                    logger.warning("Failed to get ETH rate from CoinGecko, using fallback")
                    return 2000.0  # Fallback курс
        except Exception as e:
            logger.error(f"Error getting ETH rate: {e}")
            return 2000.0  # Fallback курс

    async def get_wallet_transactions(self, wallet_address: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Получает последние транзакции кошелька"""
        try:
            # В реальной реализации здесь должен быть запрос к API блокчейна
            logger.info(f"Getting transactions for wallet {wallet_address}")
            return []
            
        except Exception as e:
            logger.error(f"Error getting transactions for {wallet_address}: {e}")
            return []
