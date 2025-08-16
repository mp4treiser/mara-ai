from celery import Celery
from celery.schedules import crontab
from src.core.config import settings

# Создаем экземпляр Celery
celery_app = Celery(
    "mara_ai",
    broker=settings.redis.url,
    backend=settings.redis.url,
    include=[
        "src.tasks.wallet_monitor"
    ]
)

# Конфигурация Celery
celery_app.conf.update(
    # Настройки Redis
    broker_connection_retry_on_startup=True,
    
    # Настройки задач
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    
    # Настройки воркеров
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
    
    # Настройки результатов
    result_expires=3600,  # 1 час
    
    # Настройки мониторинга
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 минут
    task_soft_time_limit=25 * 60,  # 25 минут
    
    # Настройки beat (планировщик)
    beat_schedule={
        # Мониторинг кошельков каждые 5 минут
        "monitor-wallets-every-5-minutes": {
            "task": "wallet_monitor.monitor_all_wallets",
            "schedule": crontab(minute="*/5"),
            "options": {"queue": "wallet_monitoring"}
        },
        
        # Мониторинг кошельков каждые 15 минут (для менее активных)
        "monitor-wallets-every-15-minutes": {
            "task": "wallet_monitor.monitor_single_wallet",
            "schedule": crontab(minute="*/15"),
            "options": {"queue": "wallet_monitoring"}
        },
        
        # Обработка pending депозитов каждые 2 минуты
        "process-pending-deposits-every-2-minutes": {
            "task": "wallet_monitor.process_pending_deposits",
            "schedule": crontab(minute="*/2"),
            "options": {"queue": "deposit_processing"}
        }
    }
)

# Настройки очередей
celery_app.conf.task_routes = {
    "wallet_monitor.monitor_all_wallets": {"queue": "wallet_monitoring"},
    "wallet_monitor.monitor_single_wallet": {"queue": "wallet_monitoring"},
    "wallet_monitor.process_deposit": {"queue": "deposit_processing"},
    "wallet_monitor.process_pending_deposits": {"queue": "deposit_processing"},
    "wallet_monitor.*": {"queue": "default"},
}

# Настройки приоритетов
celery_app.conf.task_default_priority = 5
celery_app.conf.task_queue_max_priority = 10

if __name__ == "__main__":
    celery_app.start()
