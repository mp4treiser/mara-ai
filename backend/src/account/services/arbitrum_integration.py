import asyncio
import aiohttp
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime
from src.account.models.wallet import Wallet, WalletDeposit
from web3 import Web3

logger = logging.getLogger(__name__)


class ArbitrumIntegrationService:
    """Сервис для интеграции с Arbitrum блокчейном"""
    
    def __init__(self,):
        self.arbitrum_alchemy_url = "https://arb-mainnet.g.alchemy.com/v2/gDz9efAGfWJ_Bz-siAgkr86kd2BSJGyh"
        self.arbitrum_scan_url = "https://api.etherscan.io/v2/api?chainid=42161&apikey=JMK18R5B4R2DPPGMVFF9EXRMD5ISAJH63Z"
        self.w3 = Web3(Web3.HTTPProvider("https://arb1.arbitrum.io/rpc"))
        
    async def get_wallet_balance(self, wallet_address: str) -> Dict[str, Any]:
        """Получает баланс кошелька в Arbitrum"""
        try:
            async with aiohttp.ClientSession() as session:
                # Получаем баланс ETH (Arbitrum использует ETH как нативную валюту)
                eth_balance = await self._get_eth_balance(session, wallet_address)
                
                # Получаем баланс USDT (ERC-20 токен на Arbitrum)
                usdt_balance = await self._get_usdt_balance(session, wallet_address)
                
                # Получаем курс ETH к USD
                eth_usd_rate = await self._get_eth_usd_rate(session)
                
                # Рассчитываем общий USD эквивалент
                usd_equivalent = (eth_balance * eth_usd_rate) + usdt_balance
                
                return {
                    "wallet_address": wallet_address,
                    "network": "ARBITRUM",
                    "eth_balance": eth_balance,
                    "usdt_balance": usdt_balance,
                    "usd_equivalent": usd_equivalent,
                    "last_updated": datetime.utcnow()
                }
                        
        except Exception as e:
            logger.error(f"Error getting balance for {wallet_address}: {e}")
            return {
                "wallet_address": wallet_address,
                "network": "ARBITRUM",
                "eth_balance": 0.0,
                "usdt_balance": 0.0,
                "usd_equivalent": 0.0,
                "last_updated": datetime.utcnow()
            }
    
    async def _get_eth_balance(self, session: aiohttp.ClientSession, wallet_address: str) -> float:
        """Получает баланс ETH на Arbitrum"""
        try:
            payload = {
                "jsonrpc": "2.0",
                "method": "eth_getBalance",
                "params": [wallet_address, "latest"],
                "id": 1
            }
            
            async with session.post(self.arbitrum_alchemy_url, json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    if "result" in data:
                        # Конвертируем из wei в ETH
                        wei_balance = int(data["result"], 16)
                        eth_balance = wei_balance / 10**18
                        return eth_balance
                
                return 0.0
                
        except Exception as e:
            logger.error(f"Error getting ETH balance: {e}")
            return 0.0
    
    async def _get_usdt_balance(self, session: aiohttp.ClientSession, wallet_address: str) -> float:
        """Получает баланс USDT (ERC-20 токен) на Arbitrum"""
        try:
            # USDT контракт на Arbitrum
            usdt_contract = "0xFd086bC7CD5C481DCC9C85ebE478A1C0b69FCbb9"
            
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
            
            async with session.post(self.arbitrum_alchemy_url, json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    if "result" in data and data["result"] != "0x":
                        # Конвертируем из наименьших единиц USDT (6 знаков после запятой)
                        balance_hex = data["result"]
                        balance_int = int(balance_hex, 16)
                        usdt_balance = balance_int / 10**6
                        return usdt_balance
                
                return 0.0
                
        except Exception as e:
            logger.error(f"Error getting USDT balance: {e}")
            return 0.0
    
    async def monitor_wallet_for_deposits(self, wallet: Wallet) -> List[Dict[str, Any]]:
        """Мониторит кошелек на предмет новых депозитов USDT"""
        try:
            logger.info(f"Monitoring wallet {wallet.address} for USDT deposits")

            try:
                transactions = await self.get_wallet_transactions(wallet.address, limit=50)
                logger.info(f"Total transactions received: {len(transactions)}")
                
                new_deposits = []
                usdt_transactions = 0
                
                for tx in transactions:
                    logger.info(f"Checking transaction: {tx.get('hash', 'N/A')}")
                    logger.info(f"Token name: {tx.get('tokenName', 'N/A')}")
                    logger.info(f"Token symbol: {tx.get('tokenSymbol', 'N/A')}")
                    logger.info(f"Contract address: {tx.get('contractAddress', 'N/A')}")
                    logger.info(f"To address: {tx.get('to', 'N/A')}")
                    logger.info(f"From address: {tx.get('from', 'N/A')}")
                    
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
                                new_deposits.append(deposit_data)
                                logger.info(f"✅ Found new USDT deposit: {tx.get('hash', '')} - {amount_usdt} USDT")
                            else:
                                logger.info(f"❌ Transaction is FROM our own wallet, skipping")
                        else:
                            logger.info(f"❌ Transaction is TO different address: {tx.get('to', '')}")
                    else:
                        logger.info(f"❌ Not a USDT transaction")
                
                logger.info(f"Summary: {usdt_transactions} USDT transactions found, {len(new_deposits)} new deposits")
                return new_deposits
                
            except Exception as api_error:
                logger.error(f"Arbiscan API monitoring failed: {api_error}")
                import traceback
                logger.error(f"Traceback: {traceback.format_exc()}")
                return []
            
        except Exception as e:
            logger.error(f"Error monitoring wallet {wallet.address}: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
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
                    return 0.0
        except Exception as e:
            logger.error(f"Error getting ETH rate: {e}")
            return 0.0

    async def get_wallet_transactions(self, wallet_address: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Получает последние транзакции кошелька"""
        try:
            logger.info(f"Getting transactions for wallet {wallet_address}")
            
            async with aiohttp.ClientSession() as session:
                url = self.arbitrum_scan_url
                params = {
                    'module': 'account',
                    'action': 'tokentx',
                    'address': wallet_address,
                    'startblock': 0,
                    'endblock': 99999999,
                    'page': 1,
                    'offset': limit,
                    'sort': 'desc'
                }
                
                logger.info(f"API URL: {url}")
                logger.info(f"API Params: {params}")
                
                async with session.get(url, params=params) as response:
                    logger.info(f"HTTP Status: {response.status}")
                    
                    if response.status == 200:
                        data = await response.json()
                        logger.info(f"API Response: {data}")
                        
                        if data.get('status') == '1':
                            transactions = data.get('result', [])
                            logger.info(f"Retrieved {len(transactions)} transactions for {wallet_address}")
                            
                            # Логируем каждую транзакцию
                            for i, tx in enumerate(transactions):
                                logger.info(f"Transaction {i+1}: {tx.get('hash', 'N/A')} - {tx.get('tokenName', 'N/A')} - {tx.get('value', 'N/A')}")
                            
                            return transactions
                        else:
                            logger.warning(f"Arbiscan API error: {data.get('message', 'Unknown error')}")
                            logger.warning(f"Full API response: {data}")
                            return []
                    else:
                        response_text = await response.text()
                        logger.error(f"HTTP error {response.status} getting transactions")
                        logger.error(f"Response body: {response_text}")
                        return []
                        
        except Exception as e:
            logger.error(f"Error getting transactions for {wallet_address}: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return []
