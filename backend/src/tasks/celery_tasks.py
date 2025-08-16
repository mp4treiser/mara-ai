import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any
from celery import current_task
from sqlalchemy.orm import Session
from src.core.orm.database import get_db
from src.account.services.wallet import WalletService
from src.account.repositories.wallet import WalletRepository
from src.account.models.wallet import Wallet, WalletDeposit
from src.core.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, name="monitor_all_wallets")
def monitor_all_wallets(self) -> Dict[str, Any]:
    """Мониторит все активные кошельки каждые 5 минут"""
    task_id = self.request.id
    logger.info(f"Starting wallet monitoring task {task_id}")
    
    try:
        # Получаем сессию БД
        db = next(get_db())
        wallet_repo = WalletRepository(db)
        wallet_service = WalletService(db)
        
        # Получаем кошельки для мониторинга
        wallets = wallet_repo.get_wallets_for_monitoring(limit=100)
        logger.info(f"Found {len(wallets)} wallets to monitor")
        
        results = {
            "task_id": task_id,
            "started_at": datetime.utcnow().isoformat(),
            "wallets_processed": 0,
            "new_deposits_found": 0,
            "errors": [],
            "success": True
        }
        
        for wallet in wallets:
            try:
                # Обновляем прогресс задачи
                current_task.update_state(
                    state="PROGRESS",
                    meta={
                        "current": results["wallets_processed"] + 1,
                        "total": len(wallets),
                        "wallet_address": wallet.address
                    }
                )
                
                # Мониторим кошелек (убираем await)
                new_deposits = wallet_service.monitor_wallet_transactions_sync(wallet)
                
                if new_deposits:
                    logger.info(f"Found {len(new_deposits)} new deposits for wallet {wallet.address}")
                    results["new_deposits_found"] += len(new_deposits)
                    
                    # Создаем записи о депозитах в БД
                    for deposit_data in new_deposits:
                        deposit = WalletDeposit(
                            wallet_id=wallet.id,
                            transaction_hash=deposit_data['transaction_hash'],
                            amount=deposit_data['amount'],
                            usd_amount=deposit_data['usd_amount'],
                            status=deposit_data['status'],
                            block_number=deposit_data.get('block_number')
                        )
                        wallet_repo.create_deposit(deposit)
                
                results["wallets_processed"] += 1
                
            except Exception as e:
                error_msg = f"Error monitoring wallet {wallet.address}: {str(e)}"
                logger.error(error_msg)
                results["errors"].append(error_msg)
                continue
        
        results["completed_at"] = datetime.utcnow().isoformat()
        results["duration_seconds"] = (datetime.utcnow() - datetime.fromisoformat(results["started_at"])).total_seconds()
        
        logger.info(f"Wallet monitoring task {task_id} completed. Processed {results['wallets_processed']} wallets, found {results['new_deposits_found']} new deposits")
        
        return results
        
    except Exception as e:
        error_msg = f"Fatal error in wallet monitoring task: {str(e)}"
        logger.error(error_msg)
        return {
            "task_id": task_id,
            "started_at": datetime.utcnow().isoformat(),
            "success": False,
            "error": error_msg
        }
    finally:
        if 'db' in locals():
            db.close()


@celery_app.task(bind=True, name="monitor_inactive_wallets")
def monitor_inactive_wallets(self) -> Dict[str, Any]:
    """Мониторит менее активные кошельки каждые 15 минут"""
    task_id = self.request.id
    logger.info(f"Starting inactive wallet monitoring task {task_id}")
    
    try:
        db = next(get_db())
        wallet_repo = WalletRepository(db)
        wallet_service = WalletService(db)
        
        # Получаем кошельки, которые не проверялись более 15 минут
        cutoff_time = datetime.utcnow() - timedelta(minutes=15)
        wallets = db.query(Wallet).filter(
            Wallet.is_active == True,
            (Wallet.last_checked.is_(None) | (Wallet.last_checked < cutoff_time))
        ).limit(50).all()
        
        results = {
            "task_id": task_id,
            "started_at": datetime.utcnow().isoformat(),
            "wallets_processed": 0,
            "new_deposits_found": 0,
            "errors": []
        }
        
        for wallet in wallets:
            try:
                new_deposits = wallet_service.monitor_wallet_transactions_sync(wallet)
                if new_deposits:
                    results["new_deposits_found"] += len(new_deposits)
                
                results["wallets_processed"] += 1
                
            except Exception as e:
                error_msg = f"Error monitoring inactive wallet {wallet.address}: {str(e)}"
                logger.error(error_msg)
                results["errors"].append(error_msg)
                continue
        
        results["completed_at"] = datetime.utcnow().isoformat()
        return results
        
    except Exception as e:
        logger.error(f"Fatal error in inactive wallet monitoring: {str(e)}")
        return {"success": False, "error": str(e)}
    finally:
        if 'db' in locals():
            db.close()


@celery_app.task(bind=True, name="process_pending_deposits")
def process_pending_deposits(self) -> Dict[str, Any]:
    """Обрабатывает pending депозиты каждые 2 минуты"""
    task_id = self.request.id
    logger.info(f"Starting pending deposits processing task {task_id}")
    
    try:
        db = next(get_db())
        wallet_repo = WalletRepository(db)
        wallet_service = WalletService(db)
        
        # Получаем все pending депозиты
        pending_deposits = wallet_repo.get_pending_deposits()
        
        results = {
            "task_id": task_id,
            "started_at": datetime.utcnow().isoformat(),
            "deposits_processed": 0,
            "successful_processing": 0,
            "failed_processing": 0,
            "errors": []
        }
        
        for deposit in pending_deposits:
            try:
                # Обрабатываем депозит
                success = wallet_service.process_deposit(deposit)
                
                if success:
                    results["successful_processing"] += 1
                    logger.info(f"Successfully processed deposit {deposit.transaction_hash}")
                else:
                    results["failed_processing"] += 1
                    logger.warning(f"Failed to process deposit {deposit.transaction_hash}")
                
                results["deposits_processed"] += 1
                
            except Exception as e:
                error_msg = f"Error processing deposit {deposit.transaction_hash}: {str(e)}"
                logger.error(error_msg)
                results["errors"].append(error_msg)
                results["failed_processing"] += 1
                continue
        
        results["completed_at"] = datetime.utcnow().isoformat()
        logger.info(f"Deposits processing task {task_id} completed. Processed {results['deposits_processed']} deposits")
        
        return results
        
    except Exception as e:
        logger.error(f"Fatal error in deposits processing: {str(e)}")
        return {"success": False, "error": str(e)}
    finally:
        if 'db' in locals():
            db.close()


@celery_app.task(bind=True, name="cleanup_old_logs")
def cleanup_old_logs(self) -> Dict[str, Any]:
    """Очищает старые логи и записи каждые 24 часа"""
    task_id = self.request.id
    logger.info(f"Starting cleanup task {task_id}")
    
    try:
        db = next(get_db())
        
        # Удаляем старые записи о депозитах (старше 30 дней)
        cutoff_date = datetime.utcnow() - timedelta(days=30)
        deleted_deposits = db.query(WalletDeposit).filter(
            WalletDeposit.created_at < cutoff_date,
            WalletDeposit.status.in_(["processed", "failed"])
        ).delete()
        
        # Удаляем неактивные кошельки (старше 90 дней без активности)
        cutoff_wallet = datetime.utcnow() - timedelta(days=90)
        deleted_wallets = db.query(Wallet).filter(
            Wallet.is_active == False,
            Wallet.last_checked < cutoff_wallet
        ).delete()
        
        db.commit()
        
        results = {
            "task_id": task_id,
            "started_at": datetime.utcnow().isoformat(),
            "deleted_deposits": deleted_deposits,
            "deleted_wallets": deleted_wallets,
            "completed_at": datetime.utcnow().isoformat()
        }
        
        logger.info(f"Cleanup task {task_id} completed. Deleted {deleted_deposits} deposits, {deleted_wallets} wallets")
        
        return results
        
    except Exception as e:
        logger.error(f"Fatal error in cleanup task: {str(e)}")
        return {"success": False, "error": str(e)}
    finally:
        if 'db' in locals():
            db.close()


@celery_app.task(bind=True, name="monitor_specific_wallet")
def monitor_specific_wallet(self, wallet_id: int) -> Dict[str, Any]:
    """Мониторит конкретный кошелек по требованию"""
    task_id = self.request.id
    logger.info(f"Starting specific wallet monitoring task {task_id} for wallet {wallet_id}")
    
    try:
        db = next(get_db())
        wallet_repo = WalletRepository(db)
        wallet_service = WalletService(db)
        
        wallet = wallet_repo.get_wallet_by_id(wallet_id)
        if not wallet:
            return {"success": False, "error": f"Wallet {wallet_id} not found"}
        
        # Мониторим кошелек (убираем await)
        new_deposits = wallet_service.monitor_wallet_transactions_sync(wallet)
        
        results = {
            "task_id": task_id,
            "wallet_id": wallet_id,
            "wallet_address": wallet.address,
            "new_deposits_found": len(new_deposits),
            "deposits": new_deposits,
            "completed_at": datetime.utcnow().isoformat()
        }
        
        return results
        
    except Exception as e:
        logger.error(f"Error monitoring specific wallet {wallet_id}: {str(e)}")
        return {"success": False, "error": str(e)}
    finally:
        if 'db' in locals():
            db.close()


# Функции для ручного запуска задач
def trigger_wallet_monitoring() -> str:
    """Запускает мониторинг кошельков вручную"""
    task = monitor_all_wallets.delay()
    return task.id


def trigger_deposit_processing() -> str:
    """Запускает обработку депозитов вручную"""
    task = process_pending_deposits.delay()
    return task.id


def trigger_specific_wallet_monitoring(wallet_id: int) -> str:
    """Запускает мониторинг конкретного кошелька"""
    task = monitor_specific_wallet.delay(wallet_id)
    return task.id
