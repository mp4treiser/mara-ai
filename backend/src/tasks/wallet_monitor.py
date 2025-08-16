import asyncio
import logging
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from src.core.orm.database import get_db
from src.account.services.wallet import WalletService
from src.account.repositories.wallet import WalletRepository
from src.core.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, name="wallet_monitor.monitor_all_wallets")
def monitor_all_wallets_task(self):
    """Celery задача для мониторинга всех кошельков"""
    try:
        logger.info("Starting wallet monitoring task...")
        
        # Получаем сессию БД
        db = next(get_db())
        wallet_service = WalletService(db)
        wallet_repo = WalletRepository(db)
        
        # Получаем кошельки для мониторинга
        wallets = wallet_repo.get_wallets_for_monitoring()
        logger.info(f"Found {len(wallets)} wallets to monitor")
        
        for wallet in wallets:
            try:
                # Используем синхронную версию
                new_deposits = wallet_service.monitor_wallet_transactions_sync(wallet)
                
                if new_deposits:
                    logger.info(f"Found {len(new_deposits)} new deposits for wallet {wallet.address}")
                    
                    # Обрабатываем каждое пополнение
                    for deposit in new_deposits:
                        success = wallet_service.process_deposit(deposit)
                        if success:
                            logger.info(f"Successfully processed deposit {deposit.transaction_hash}")
                        else:
                            logger.error(f"Failed to process deposit {deposit.transaction_hash}")
                else:
                    logger.debug(f"No new deposits for wallet {wallet.address}")
                    
            except Exception as e:
                logger.error(f"Error monitoring wallet {wallet.address}: {e}")
                continue
        
        logger.info("Wallet monitoring task completed")
        return {"success": True, "wallets_processed": len(wallets)}
        
    except Exception as e:
        logger.error(f"Error in wallet monitoring task: {e}")
        return {"success": False, "error": str(e)}
    finally:
        if 'db' in locals():
            db.close()


@celery_app.task(bind=True, name="wallet_monitor.process_deposit")
def process_deposit_task(self, deposit_id: int):
    """Celery задача для обработки конкретного депозита"""
    try:
        logger.info(f"Processing deposit {deposit_id}")
        
        # Получаем сессию БД
        db = next(get_db())
        wallet_service = WalletService(db)
        wallet_repo = WalletRepository(db)
        
        # Получаем депозит по ID
        deposit = wallet_repo.get_deposit_by_id(deposit_id)
        if not deposit:
            logger.error(f"Deposit {deposit_id} not found")
            return {"success": False, "error": "Deposit not found"}
        
        # Обрабатываем пополнение
        success = wallet_service.process_deposit(deposit)
        
        if success:
            logger.info(f"Successfully processed deposit {deposit.transaction_hash}")
            return {"success": True, "deposit_id": deposit_id}
        else:
            logger.error(f"Failed to process deposit {deposit.transaction_hash}")
            return {"success": False, "error": "Processing failed"}
            
    except Exception as e:
        logger.error(f"Error processing deposit {deposit_id}: {e}")
        return {"success": False, "error": str(e)}
    finally:
        if 'db' in locals():
            db.close()


@celery_app.task(bind=True, name="wallet_monitor.process_pending_deposits")
def process_pending_deposits_task(self):
    """Celery задача для обработки всех pending депозитов"""
    try:
        logger.info("Starting pending deposits processing task...")
        
        # Получаем сессию БД
        db = next(get_db())
        wallet_service = WalletService(db)
        wallet_repo = WalletRepository(db)
        
        # Получаем все pending депозиты
        pending_deposits = wallet_repo.get_pending_deposits()
        logger.info(f"Found {len(pending_deposits)} pending deposits")
        
        processed_count = 0
        failed_count = 0
        
        for deposit in pending_deposits:
            try:
                # Обрабатываем пополнение
                success = wallet_service.process_deposit(deposit)
                
                if success:
                    logger.info(f"Successfully processed deposit {deposit.transaction_hash}")
                    processed_count += 1
                else:
                    logger.error(f"Failed to process deposit {deposit.transaction_hash}")
                    failed_count += 1
                    
            except Exception as e:
                logger.error(f"Error processing deposit {deposit.transaction_hash}: {e}")
                failed_count += 1
                continue
        
        logger.info(f"Pending deposits processing completed. Processed: {processed_count}, Failed: {failed_count}")
        return {
            "success": True, 
            "processed_count": processed_count, 
            "failed_count": failed_count,
            "total_count": len(pending_deposits)
        }
        
    except Exception as e:
        logger.error(f"Error in pending deposits processing task: {e}")
        return {"success": False, "error": str(e)}
    finally:
        if 'db' in locals():
            db.close()


@celery_app.task(bind=True, name="wallet_monitor.monitor_single_wallet")
def monitor_single_wallet_task(self, wallet_id: int):
    """Celery задача для мониторинга конкретного кошелька"""
    try:
        logger.info(f"Monitoring single wallet {wallet_id}")
        
        # Получаем сессию БД
        db = next(get_db())
        wallet_service = WalletService(db)
        wallet_repo = WalletRepository(db)
        
        # Получаем кошелек по ID
        wallet = wallet_repo.get_wallet_by_id(wallet_id)
        if not wallet:
            logger.error(f"Wallet {wallet_id} not found")
            return {"success": False, "error": "Wallet not found"}
        
        # Мониторим транзакции кошелька
        new_deposits = wallet_service.monitor_wallet_transactions_sync(wallet)
        
        if new_deposits:
            logger.info(f"Found {len(new_deposits)} new deposits for wallet {wallet.address}")
            
            # Обрабатываем каждое пополнение
            for deposit in new_deposits:
                success = wallet_service.process_deposit(deposit)
                if success:
                    logger.info(f"Successfully processed deposit {deposit.transaction_hash}")
                else:
                    logger.error(f"Failed to process deposit {deposit.transaction_hash}")
        else:
            logger.debug(f"No new deposits for wallet {wallet.address}")
        
        return {"success": True, "wallet_id": wallet_id, "new_deposits": len(new_deposits)}
        
    except Exception as e:
        logger.error(f"Error monitoring wallet {wallet_id}: {e}")
        return {"success": False, "error": str(e)}
    finally:
        if 'db' in locals():
            db.close()


# Функции для ручного запуска задач
def trigger_wallet_monitoring() -> str:
    """Запускает мониторинг кошельков вручную"""
    task = monitor_all_wallets_task.delay()
    return task.id


def trigger_deposit_processing(deposit_id: int) -> str:
    """Запускает обработку конкретного депозита"""
    task = process_deposit_task.delay(deposit_id)
    return task.id


def trigger_single_wallet_monitoring(wallet_id: int) -> str:
    """Запускает мониторинг конкретного кошелька"""
    task = monitor_single_wallet_task.delay(wallet_id)
    return task.id
