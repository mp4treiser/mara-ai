import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, List

from src.core.orm.database import get_async_session
from src.core.middlewares.subscription_middleware import require_active_subscription
from src.account.models.user import User
from src.agents.repositories.telegram_config import TelegramConfigRepository
from src.agents.repositories.telegram_monitored_chat import TelegramMonitoredChatRepository

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/user/agents", tags=["aiogram-bot-management"])


@router.get("/{agent_id}/aiogram-bot/status")
async def get_aiogram_bot_status(
    agent_id: int,
    current_user: User = Depends(require_active_subscription),
    db: AsyncSession = Depends(get_async_session)
):
    """Получает статус aiogram бота"""
    try:
        # Проверяем, что у пользователя есть Telegram конфигурация
        telegram_repo = TelegramConfigRepository(db)
        config = await telegram_repo.get_by_agent_id(agent_id)
        
        if not config or config.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Telegram конфигурация не найдена"
            )
        
        # Получаем количество мониторимых чатов
        monitoring_repo = TelegramMonitoredChatRepository(db)
        monitored_chats = await monitoring_repo.get_by_config_id(config.id)
        active_chats_count = len([chat for chat in monitored_chats if chat.is_active])
        
        return {
            "bot_token": config.bot_token[:10] + "...",
            "is_active": config.is_active,
            "monitored_chats_count": active_chats_count,
            "chat_ids": [chat.chat_id for chat in monitored_chats if chat.is_active]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка при получении статуса aiogram бота: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при получении статуса aiogram бота: {str(e)}"
        )


@router.post("/{agent_id}/aiogram-bot/restart")
async def restart_aiogram_bot(
    agent_id: int,
    current_user: User = Depends(require_active_subscription),
    db: AsyncSession = Depends(get_async_session)
):
    """Перезапускает aiogram бота (требует перезапуска контейнера)"""
    try:
        # Проверяем, что у пользователя есть Telegram конфигурация
        telegram_repo = TelegramConfigRepository(db)
        config = await telegram_repo.get_by_agent_id(agent_id)
        
        if not config or config.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Telegram конфигурация не найдена"
            )
        
        # В реальном приложении здесь можно добавить логику для перезапуска контейнера
        # Пока просто возвращаем информацию
        return {
            "message": "Для перезапуска aiogram бота необходимо перезапустить контейнер aiogram-bot",
            "command": "docker-compose restart aiogram-bot"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка при перезапуске aiogram бота: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при перезапуске aiogram бота: {str(e)}"
        )


@router.get("/aiogram-bots/status")
async def get_all_aiogram_bots_status(
    current_user: User = Depends(require_active_subscription),
    db: AsyncSession = Depends(get_async_session)
):
    """Получает статус всех aiogram ботов пользователя"""
    try:
        # Получаем все конфигурации пользователя
        telegram_repo = TelegramConfigRepository(db)
        configs = await telegram_repo.get_by_user_id(current_user.id)
        
        bots_status = []
        for config in configs:
            monitoring_repo = TelegramMonitoredChatRepository(db)
            monitored_chats = await monitoring_repo.get_by_config_id(config.id)
            active_chats_count = len([chat for chat in monitored_chats if chat.is_active])
            
            bots_status.append({
                "agent_id": config.agent_id,
                "bot_token": config.bot_token[:10] + "...",
                "is_active": config.is_active,
                "monitored_chats_count": active_chats_count,
                "chat_ids": [chat.chat_id for chat in monitored_chats if chat.is_active]
            })
        
        return {
            "bots": bots_status,
            "total_bots": len(configs)
        }
        
    except Exception as e:
        logger.error(f"Ошибка при получении статуса aiogram ботов: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при получении статуса aiogram ботов: {str(e)}"
        )
