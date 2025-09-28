import asyncio
import aiohttp
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, select
from src.core.orm.database import SessionLocal
from src.account.services.wallet import WalletService
from src.account.models.wallet import Wallet, WalletDeposit
from src.core.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, name="arbitrum_tasks.monitor_arbitrum_wallets")
def monitor_arbitrum_wallets_task(self):
    """Celery задача для мониторинга Arbitrum кошельков"""
    try:
        logger.info("Starting Arbitrum wallet monitoring task...")
        
        with SessionLocal() as db:
            wallet_service = WalletService(db)
            
            # Получаем только ARBITRUM кошельки
            cutoff_time = datetime.utcnow() - timedelta(minutes=5)
            wallets = db.query(Wallet).filter(
                and_(
                    Wallet.is_active == True,
                    Wallet.network == "ARBITRUM",
                    (Wallet.last_checked.is_(None) | (Wallet.last_checked < cutoff_time))
                )
            ).limit(50).all()
            
            logger.info(f"Found {len(wallets)} Arbitrum wallets to monitor")
            
            total_deposits = 0
            for wallet in wallets:
                try:
                    # Мониторим новые депозиты (используем синхронную версию)
                    new_deposits = wallet_service.monitor_wallet_transactions_sync(wallet)
                    
                    if new_deposits:
                        logger.info(f"Found {len(new_deposits)} new deposits for wallet {wallet.address}")
                        total_deposits += len(new_deposits)
                        
                        # Обрабатываем каждое пополнение
                        for deposit in new_deposits:
                            success = wallet_service.process_deposit(deposit)
                            if success:
                                logger.info(f"Successfully processed deposit {deposit.transaction_hash}")
                            else:
                                logger.error(f"Failed to process deposit {deposit.transaction_hash}")
                    else:
                        logger.debug(f"No new deposits for wallet {wallet.address}")
                    
                    # Обновляем время последней проверки
                    wallet.last_checked = datetime.utcnow()
                    db.commit()
                        
                except Exception as e:
                    logger.error(f"Error monitoring Arbitrum wallet {wallet.address}: {e}")
                    continue
            
            logger.info(f"Arbitrum monitoring completed. Total new deposits: {total_deposits}")
            return {
                "success": True, 
                "wallets_processed": len(wallets),
                "new_deposits": total_deposits
            }
        
    except Exception as e:
        logger.error(f"Error in Arbitrum monitoring task: {e}")
        return {"success": False, "error": str(e)}


@celery_app.task(bind=True, name="arbitrum_tasks.update_arbitrum_balances")
def update_arbitrum_balances_task(self):
    """Celery задача для обновления балансов Arbitrum кошельков"""
    try:
        logger.info("Starting Arbitrum balance update task...")
        
        with SessionLocal() as db:
            wallet_service = WalletService(db)
            
            # Получаем все активные ARBITRUM кошельки
            wallets = db.query(Wallet).filter(
                and_(
                    Wallet.is_active == True,
                    Wallet.network == "ARBITRUM"
                )
            ).all()
            
            logger.info(f"Found {len(wallets)} Arbitrum wallets to update balances")
            
            updated_count = 0
            total_usd_value = 0.0
            
            for wallet in wallets:
                try:
                    # Получаем актуальный баланс
                    balance_info = asyncio.run(wallet_service.get_wallet_balance(wallet))
                    
                    usd_value = balance_info.get('usd_equivalent', 0)
                    total_usd_value += usd_value
                    
                    logger.info(f"Wallet {wallet.address}: {balance_info.get('eth_balance', 0)} ETH, "
                              f"{balance_info.get('usdt_balance', 0)} USDT, "
                              f"${usd_value:.2f} USD")
                    
                    updated_count += 1
                    
                except Exception as e:
                    logger.error(f"Error updating balance for wallet {wallet.address}: {e}")
                    continue
            
            logger.info(f"Balance update completed. Updated: {updated_count}, Total USD value: ${total_usd_value:.2f}")
            return {
                "success": True,
                "wallets_updated": updated_count,
                "total_usd_value": total_usd_value
            }
        
    except Exception as e:
        logger.error(f"Error in balance update task: {e}")
        return {"success": False, "error": str(e)}


@celery_app.task(bind=True, name="arbitrum_tasks.process_arbitrum_deposits")
def process_arbitrum_deposits_task(self):
    """Celery задача для обработки депозитов на Arbitrum"""
    try:
        logger.info("Starting Arbitrum deposits processing task...")
        
        with SessionLocal() as db:
            wallet_service = WalletService(db)
            
            # Получаем все pending депозиты для ARBITRUM кошельков
            pending_deposits = db.query(WalletDeposit).join(Wallet).filter(
                and_(
                    WalletDeposit.status == "pending",
                    Wallet.network == "ARBITRUM"
                )
            ).all()
            
            logger.info(f"Found {len(pending_deposits)} pending Arbitrum deposits")
            
            processed_count = 0
            failed_count = 0
            
            for deposit in pending_deposits:
                try:
                    # Обрабатываем депозит
                    success = wallet_service.process_deposit(deposit)
                    
                    if success:
                        logger.info(f"Successfully processed Arbitrum deposit {deposit.transaction_hash}")
                        processed_count += 1
                    else:
                        logger.error(f"Failed to process Arbitrum deposit {deposit.transaction_hash}")
                        failed_count += 1
                        
                except Exception as e:
                    logger.error(f"Error processing Arbitrum deposit {deposit.transaction_hash}: {e}")
                    failed_count += 1
                    continue
            
            logger.info(f"Arbitrum deposits processing completed. Processed: {processed_count}, Failed: {failed_count}")
            return {
                "success": True,
                "processed_count": processed_count,
                "failed_count": failed_count,
                "total_count": len(pending_deposits)
            }
        
    except Exception as e:
        logger.error(f"Error in Arbitrum deposits processing task: {e}")
        return {"success": False, "error": str(e)}


@celery_app.task(bind=True, name="arbitrum_tasks.monitor_arbitrum_transactions")
def monitor_arbitrum_transactions_task(self, wallet_address: str):
    """Celery задача для мониторинга транзакций конкретного Arbitrum кошелька"""
    try:
        logger.info(f"Monitoring Arbitrum transactions for wallet {wallet_address}")
        
        with SessionLocal() as db:
            wallet_service = WalletService(db)
            
            # Получаем кошелек
            wallet = db.query(Wallet).filter(
                and_(
                    Wallet.address == wallet_address,
                    Wallet.network == "ARBITRUM"
                )
            ).first()
            
            if not wallet:
                logger.error(f"Arbitrum wallet {wallet_address} not found")
                return {"success": False, "error": "Wallet not found"}
            
            # Мониторим транзакции
            new_deposits = asyncio.run(wallet_service.monitor_wallet_transactions(wallet))
            
            if new_deposits:
                logger.info(f"Found {len(new_deposits)} new transactions for wallet {wallet_address}")
                
                # Обрабатываем каждое пополнение
                for deposit in new_deposits:
                    success = wallet_service.process_deposit(deposit)
                    if success:
                        logger.info(f"Successfully processed transaction {deposit.transaction_hash}")
                    else:
                        logger.error(f"Failed to process transaction {deposit.transaction_hash}")
            else:
                logger.debug(f"No new transactions for wallet {wallet_address}")
            
            return {
                "success": True,
                "wallet_address": wallet_address,
                "new_transactions": len(new_deposits)
            }
        
    except Exception as e:
        logger.error(f"Error monitoring Arbitrum transactions for {wallet_address}: {e}")
        return {"success": False, "error": str(e)}


# Функции для ручного запуска задач
def trigger_arbitrum_monitoring() -> str:
    """Запускает мониторинг Arbitrum кошельков вручную"""
    task = monitor_arbitrum_wallets_task.delay()
    return task.id


def trigger_arbitrum_balance_update() -> str:
    """Запускает обновление балансов Arbitrum кошельков вручную"""
    task = update_arbitrum_balances_task.delay()
    return task.id


def trigger_arbitrum_deposits_processing() -> str:
    """Запускает обработку депозитов Arbitrum вручную"""
    task = process_arbitrum_deposits_task.delay()
    return task.id


def trigger_arbitrum_transactions_monitoring(wallet_address: str) -> str:
    """Запускает мониторинг транзакций конкретного Arbitrum кошелька"""
    task = monitor_arbitrum_transactions_task.delay(wallet_address)
    return task.id
