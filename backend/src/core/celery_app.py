from celery import Celery
from celery.schedules import crontab
from src.core.config import settings

# Создаем экземпляр Celery
celery_app = Celery(
    "mara_ai",
    broker=settings.redis.url,
    backend=settings.redis.url,
    include=[
        #"src.tasks.wallet_monitor",
        "src.tasks.arbitrum_tasks",
        "src.tasks.telegram_tasks",
        "src.tasks.subscription_tasks",
        "src.tasks.document_tasks",
        "src.tasks.telegram_alert_tasks",
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
        # Мониторинг Arbitrum кошельков каждые 3 минуты
        "monitor-arbitrum-wallets-every-3-minutes": {
            "task": "arbitrum_tasks.monitor_arbitrum_wallets",
            "schedule": crontab(minute="*/3"),
            "options": {"queue": "arbitrum_monitoring"}
        },
        
        # Обновление балансов Arbitrum каждые 10 минут
        "update-arbitrum-balances-every-10-minutes": {
            "task": "arbitrum_tasks.update_arbitrum_balances",
            "schedule": crontab(minute="*/10"),
            "options": {"queue": "arbitrum_monitoring"}
        },
        
        # Обработка Arbitrum депозитов каждые 2 минуты
        "process-arbitrum-deposits-every-2-minutes": {
            "task": "arbitrum_tasks.process_arbitrum_deposits",
            "schedule": crontab(minute="*/2"),
            "options": {"queue": "arbitrum_processing"}
        },
        
        # Деактивация истекших подписок каждый день в 8:00
        "deactivate-expired-subscriptions-daily": {
            "task": "subscription_tasks.deactivate_expired_subscriptions",
            "schedule": crontab(hour=0, minute=10),
            "options": {"queue": "subscription_management"}
        }
    }
)

# Настройки очередей
celery_app.conf.task_routes = {
    # Arbitrum задачи
    "arbitrum_tasks.monitor_arbitrum_wallets": {"queue": "arbitrum_monitoring"},
    "arbitrum_tasks.update_arbitrum_balances": {"queue": "arbitrum_monitoring"},
    "arbitrum_tasks.process_arbitrum_deposits": {"queue": "arbitrum_processing"},
    "arbitrum_tasks.monitor_arbitrum_transactions": {"queue": "arbitrum_monitoring"},
    "arbitrum_tasks.*": {"queue": "arbitrum_monitoring"},
    
    # Старые задачи кошельков (для совместимости)
    # "wallet_monitor.monitor_all_wallets": {"queue": "wallet_monitoring"},
    # "wallet_monitor.monitor_single_wallet": {"queue": "wallet_monitoring"},
    # "wallet_monitor.process_deposit": {"queue": "deposit_processing"},
    # "wallet_monitor.process_pending_deposits": {"queue": "deposit_processing"},
    # "wallet_monitor.*": {"queue": "default"},
    
    # Telegram задачи
    "telegram_tasks.send_telegram_notification": {"queue": "telegram_notifications"},
    "telegram_tasks.send_telegram_test_message": {"queue": "telegram_notifications"},
    "telegram_tasks.send_subscription_notification": {"queue": "telegram_notifications"},
    "telegram_tasks.*": {"queue": "default"},
    
    # Подписки
    "subscription_tasks.deactivate_expired_subscriptions": {"queue": "subscription_management"},
    "subscription_tasks.*": {"queue": "default"},
    
    # Документы
    "document_tasks.process_document_task": {"queue": "default"},
    "document_tasks.delete_document_from_vector_store_task": {"queue": "default"},
    "document_tasks.*": {"queue": "default"},
    
    # Telegram алерты
    "telegram_alert_tasks.process_telegram_alert_task": {"queue": "telegram_notifications"},
    "telegram_alert_tasks.*": {"queue": "telegram_notifications"},
    
}

# Настройки приоритетов
celery_app.conf.task_default_priority = 5
celery_app.conf.task_queue_max_priority = 10

if __name__ == "__main__":
    celery_app.start()
