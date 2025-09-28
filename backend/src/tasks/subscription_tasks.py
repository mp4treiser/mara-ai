import logging
from datetime import datetime
from sqlalchemy.orm import Session
from src.core.orm.database import SessionLocal
from src.core.celery_app import celery_app
from src.account.models.subscription import Subscription
logger = logging.getLogger(__name__)


@celery_app.task(bind=True, name="subscription_tasks.deactivate_expired_subscriptions")
def deactivate_expired_subscriptions(self):
    """
    Celery задача для деактивации истекших подписок.
    Запускается ежедневно.
    """
    logger.info("Начинаем деактивацию истекших подписок")
    
    try:
        with SessionLocal() as db:
            today = datetime.now().date()
            
            # Находим истекшие подписки через ORM
            expired_subscriptions = db.query(Subscription).filter(
                Subscription.is_active == True,
                Subscription.end_date <= today
            ).all()
            
            logger.info(f"Найдено {len(expired_subscriptions)} истекших подписок")
            
            deactivated_count = 0
            for subscription in expired_subscriptions:
                # Деактивируем подписку через ORM
                subscription.is_active = False
                deactivated_count += 1
                logger.info(f"Деактивирована подписка {subscription.id} (пользователь {subscription.user_id}, истекает {subscription.end_date})")
            
            db.commit()
            logger.info(f"Деактивировано подписок: {deactivated_count}")
            
        logger.info("Деактивация истекших подписок завершена")
        return {"success": True, "deactivated_count": deactivated_count}
        
    except Exception as e:
        logger.error(f"Ошибка при деактивации подписок: {e}")
        raise
