import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from src.core.orm.database import get_async_session
from src.core.middlewares.subscription_middleware import require_active_subscription
from src.account.models.user import User
from src.agents.schemas.telegram_monitored_chat import (
    TelegramMonitoredChatCreate, TelegramMonitoredChatUpdate, TelegramMonitoredChatResponse
)
from src.agents.repositories.telegram_monitored_chat import TelegramMonitoredChatRepository
from src.agents.repositories.telegram_config import TelegramConfigRepository

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/user/agents", tags=["telegram-monitoring"])


@router.post("/{agent_id}/telegram-config/monitored-chats", response_model=TelegramMonitoredChatResponse)
async def create_monitored_chat(
    agent_id: int,
    chat_data: TelegramMonitoredChatCreate,
    current_user: User = Depends(require_active_subscription),
    db: AsyncSession = Depends(get_async_session)
):
    """Создает новый мониторинг чата для агента"""
    try:
        # Проверяем, что у пользователя есть доступ к агенту и Telegram конфигурации
        telegram_repo = TelegramConfigRepository(db)
        telegram_config = await telegram_repo.get_by_agent_id(agent_id)
        
        if not telegram_config or telegram_config.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Telegram конфигурация не найдена"
            )
        
        # Проверяем, что чат еще не мониторится
        monitoring_repo = TelegramMonitoredChatRepository(db)
        existing_chats = await monitoring_repo.get_by_config_id(telegram_config.id)
        
        for chat in existing_chats:
            if chat.chat_id == chat_data.chat_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Этот чат уже мониторится"
                )
        
        # Создаем мониторинг
        monitored_chat = await monitoring_repo.create(telegram_config.id, chat_data)
        
        # Обновляем мониторинг для aiogram бота
        import aiohttp
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    "http://aiogram-bot:8001/update-monitoring",
                    json={"bot_token": telegram_config.bot_token}
                ) as response:
                    if response.status != 200:
                        logger.warning(f"Failed to update aiogram bot monitoring: {response.status}")
        except Exception as e:
            logger.warning(f"Failed to update aiogram bot monitoring: {e}")
        
        return TelegramMonitoredChatResponse(
            id=monitored_chat.id,
            telegram_config_id=monitored_chat.telegram_config_id,
            chat_id=monitored_chat.chat_id,
            chat_title=monitored_chat.chat_title,
            chat_type=monitored_chat.chat_type,
            is_active=monitored_chat.is_active,
            keywords=monitored_chat.keywords,
            created_at=monitored_chat.created_at,
            updated_at=monitored_chat.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка при создании мониторинга чата: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при создании мониторинга: {str(e)}"
        )


@router.get("/{agent_id}/telegram-config/monitored-chats", response_model=List[TelegramMonitoredChatResponse])
async def get_monitored_chats(
    agent_id: int,
    current_user: User = Depends(require_active_subscription),
    db: AsyncSession = Depends(get_async_session)
):
    """Получает список мониторингов чатов для агента"""
    try:
        # Проверяем доступ к Telegram конфигурации
        telegram_repo = TelegramConfigRepository(db)
        telegram_config = await telegram_repo.get_by_agent_id(agent_id)
        
        if not telegram_config or telegram_config.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Telegram конфигурация не найдена"
            )
        
        # Получаем мониторинги
        monitoring_repo = TelegramMonitoredChatRepository(db)
        monitored_chats = await monitoring_repo.get_by_config_id(telegram_config.id)
        
        return [
            TelegramMonitoredChatResponse(
                id=chat.id,
                telegram_config_id=chat.telegram_config_id,
                chat_id=chat.chat_id,
                chat_title=chat.chat_title,
                chat_type=chat.chat_type,
                is_active=chat.is_active,
                keywords=chat.keywords,
                created_at=chat.created_at,
                updated_at=chat.updated_at
            )
            for chat in monitored_chats
        ]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка при получении мониторингов чатов: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при получении мониторингов: {str(e)}"
        )


@router.put("/{agent_id}/telegram-config/monitored-chats/{chat_id}", response_model=TelegramMonitoredChatResponse)
async def update_monitored_chat(
    agent_id: int,
    chat_id: int,
    chat_data: TelegramMonitoredChatUpdate,
    current_user: User = Depends(require_active_subscription),
    db: AsyncSession = Depends(get_async_session)
):
    """Обновляет мониторинг чата"""
    try:
        # Проверяем доступ к Telegram конфигурации
        telegram_repo = TelegramConfigRepository(db)
        telegram_config = await telegram_repo.get_by_agent_id(agent_id)
        
        if not telegram_config or telegram_config.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Telegram конфигурация не найдена"
            )
        
        # Проверяем, что мониторинг существует и принадлежит пользователю
        monitoring_repo = TelegramMonitoredChatRepository(db)
        monitored_chat = await monitoring_repo.get_by_id(chat_id)
        
        if not monitored_chat or monitored_chat.telegram_config_id != telegram_config.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Мониторинг чата не найден"
            )
        
        # Обновляем мониторинг
        updated_chat = await monitoring_repo.update(chat_id, chat_data)
        
        if not updated_chat:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Не удалось обновить мониторинг"
            )
        
        return TelegramMonitoredChatResponse(
            id=updated_chat.id,
            telegram_config_id=updated_chat.telegram_config_id,
            chat_id=updated_chat.chat_id,
            chat_title=updated_chat.chat_title,
            chat_type=updated_chat.chat_type,
            is_active=updated_chat.is_active,
            keywords=updated_chat.keywords,
            created_at=updated_chat.created_at,
            updated_at=updated_chat.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка при обновлении мониторинга чата: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при обновлении мониторинга: {str(e)}"
        )


@router.delete("/{agent_id}/telegram-config/monitored-chats/{chat_id}")
async def delete_monitored_chat(
    agent_id: int,
    chat_id: int,
    current_user: User = Depends(require_active_subscription),
    db: AsyncSession = Depends(get_async_session)
):
    """Удаляет мониторинг чата"""
    try:
        # Проверяем доступ к Telegram конфигурации
        telegram_repo = TelegramConfigRepository(db)
        telegram_config = await telegram_repo.get_by_agent_id(agent_id)
        
        if not telegram_config or telegram_config.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Telegram конфигурация не найдена"
            )
        
        # Проверяем, что мониторинг существует и принадлежит пользователю
        monitoring_repo = TelegramMonitoredChatRepository(db)
        monitored_chat = await monitoring_repo.get_by_id(chat_id)
        
        if not monitored_chat or monitored_chat.telegram_config_id != telegram_config.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Мониторинг чата не найден"
            )
        
        # Удаляем мониторинг
        success = await monitoring_repo.delete(chat_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Не удалось удалить мониторинг"
            )
        
        # Обновляем мониторинг для aiogram бота
        import aiohttp
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    "http://aiogram-bot:8001/update-monitoring",
                    json={"bot_token": telegram_config.bot_token}
                ) as response:
                    if response.status != 200:
                        logger.warning(f"Failed to update aiogram bot monitoring: {response.status}")
        except Exception as e:
            logger.warning(f"Failed to update aiogram bot monitoring: {e}")
        
        return {"message": "Мониторинг чата успешно удален"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка при удалении мониторинга чата: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при удалении мониторинга: {str(e)}"
        )


@router.post("/{agent_id}/telegram-config/monitored-chats/{chat_id}/test")
async def test_monitored_chat(
    agent_id: int,
    chat_id: int,
    current_user: User = Depends(require_active_subscription),
    db: AsyncSession = Depends(get_async_session)
):
    """Тестирует мониторинг чата - отправляет тестовое сообщение"""
    try:
        # Проверяем доступ к Telegram конфигурации
        telegram_repo = TelegramConfigRepository(db)
        telegram_config = await telegram_repo.get_by_agent_id(agent_id)
        
        if not telegram_config or telegram_config.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Telegram конфигурация не найдена"
            )
        
        # Проверяем, что мониторинг существует
        monitoring_repo = TelegramMonitoredChatRepository(db)
        monitored_chat = await monitoring_repo.get_by_id(chat_id)
        
        if not monitored_chat or monitored_chat.telegram_config_id != telegram_config.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Мониторинг чата не найден"
            )
        
        # Отправляем тестовое сообщение в чат для отправки
        from src.agents.services.telegram_service import TelegramService, TelegramMessage
        
        telegram_service = TelegramService()
        
        test_message = f"""
🔍 <b>Тест мониторинга чата</b>

Мониторинг чата: {monitored_chat.chat_title or monitored_chat.chat_id}
Тип чата: {monitored_chat.chat_type}
Ключевые слова: {', '.join(monitored_chat.keywords) if monitored_chat.keywords else 'Не заданы'}

---
<i>Это тестовое сообщение подтверждает, что мониторинг настроен корректно.</i>
        """.strip()
        
        message = TelegramMessage(
            chat_id=telegram_config.chat_id,
            text=test_message,
            parse_mode="HTML"
        )
        
        result = await telegram_service.send_message(telegram_config.bot_token, message)
        
        return {
            "success": True,
            "message": "Тестовое сообщение отправлено успешно",
            "telegram_message_id": result.get("result", {}).get("message_id")
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка при тестировании мониторинга чата: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при тестировании мониторинга: {str(e)}"
        )
