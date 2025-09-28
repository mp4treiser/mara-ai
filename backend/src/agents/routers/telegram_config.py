import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from src.core.orm.database import get_async_session
from src.core.dependencies import get_current_user
from src.core.middlewares.subscription_middleware import require_active_subscription
from src.account.models.user import User
from src.agents.schemas.telegram_config import (
    TelegramConfigCreate, TelegramConfigUpdate, TelegramConfigResponse,
    TelegramTestMessage, TelegramSendMessage
)
from src.agents.repositories.telegram_config import TelegramConfigRepository
from src.agents.services.telegram_service import TelegramService
from src.agents.repositories.user_agent import UserAgentRepository

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/user/agents", tags=["telegram-config"])

# Инициализируем сервис
telegram_service = TelegramService()


@router.post("/{agent_id}/telegram-config", response_model=TelegramConfigResponse)
async def create_telegram_config(
    agent_id: int,
    config_data: TelegramConfigCreate,
    current_user: User = Depends(require_active_subscription),
    db: AsyncSession = Depends(get_async_session)
):
    """
    Создает Telegram конфигурацию для агента.
    Требует активную подписку.
    """
    try:
        # Проверяем, что пользователь имеет доступ к агенту
        user_agent_repo = UserAgentRepository(db)
        user_agent = await user_agent_repo.get_by_user_and_agent(current_user.id, agent_id)
        
        if not user_agent or not user_agent.is_active:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Агент не найден или недоступен"
            )
        
        # Проверяем, что конфигурация еще не существует
        telegram_repo = TelegramConfigRepository(db)
        existing_config = await telegram_repo.get_by_agent_id(agent_id)
        
        if existing_config:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Telegram конфигурация для этого агента уже существует"
            )
        
        # Валидируем токен бота
        if not telegram_service.validate_bot_token(config_data.bot_token):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Неверный формат токена бота"
            )
        
        # Валидируем chat_id
        if not telegram_service.validate_chat_id(config_data.chat_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Неверный формат ID чата"
            )
        
        # Тестируем подключение к боту
        bot_connection_ok = await telegram_service.test_bot_connection(config_data.bot_token)
        if not bot_connection_ok:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Не удалось подключиться к боту. Проверьте токен."
            )
        
        # Создаем конфигурацию
        config = await telegram_repo.create(config_data, agent_id, current_user.id)
        
        return TelegramConfigResponse(
            id=config.id,
            agent_id=config.agent_id,
            user_id=config.user_id,
            bot_token=config.bot_token,  # Будет замаскирован в схеме
            chat_id=config.chat_id,
            is_active=config.is_active,
            created_at=config.created_at,
            updated_at=config.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка при создании Telegram конфигурации: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при создании конфигурации: {str(e)}"
        )


@router.get("/{agent_id}/telegram-config", response_model=TelegramConfigResponse)
async def get_telegram_config(
    agent_id: int,
    current_user: User = Depends(require_active_subscription),
    db: AsyncSession = Depends(get_async_session)
):
    """
    Получает Telegram конфигурацию агента.
    Требует активную подписку.
    """
    try:
        # Проверяем доступ к агенту
        user_agent_repo = UserAgentRepository(db)
        user_agent = await user_agent_repo.get_by_user_and_agent(current_user.id, agent_id)
        
        if not user_agent or not user_agent.is_active:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Агент не найден или недоступен"
            )
        
        # Получаем конфигурацию
        telegram_repo = TelegramConfigRepository(db)
        config = await telegram_repo.get_by_agent_id(agent_id)
        
        if not config:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Telegram конфигурация не найдена"
            )
        
        return TelegramConfigResponse(
            id=config.id,
            agent_id=config.agent_id,
            user_id=config.user_id,
            bot_token=config.bot_token,
            chat_id=config.chat_id,
            is_active=config.is_active,
            created_at=config.created_at,
            updated_at=config.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка при получении Telegram конфигурации: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при получении конфигурации: {str(e)}"
        )


@router.put("/{agent_id}/telegram-config", response_model=TelegramConfigResponse)
async def update_telegram_config(
    agent_id: int,
    config_data: TelegramConfigUpdate,
    current_user: User = Depends(require_active_subscription),
    db: AsyncSession = Depends(get_async_session)
):
    """
    Обновляет Telegram конфигурацию агента.
    Требует активную подписку.
    """
    try:
        # Проверяем доступ к агенту
        user_agent_repo = UserAgentRepository(db)
        user_agent = await user_agent_repo.get_by_user_and_agent(current_user.id, agent_id)
        
        if not user_agent or not user_agent.is_active:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Агент не найден или недоступен"
            )
        
        # Получаем существующую конфигурацию
        telegram_repo = TelegramConfigRepository(db)
        config = await telegram_repo.get_by_agent_id(agent_id)
        
        if not config:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Telegram конфигурация не найдена"
            )
        
        # Валидируем новые данные если они предоставлены
        if config_data.bot_token and not telegram_service.validate_bot_token(config_data.bot_token):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Неверный формат токена бота"
            )
        
        if config_data.chat_id and not telegram_service.validate_chat_id(config_data.chat_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Неверный формат ID чата"
            )
        
        # Если обновляется токен, тестируем подключение
        if config_data.bot_token:
            bot_connection_ok = await telegram_service.test_bot_connection(config_data.bot_token)
            if not bot_connection_ok:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Не удалось подключиться к боту. Проверьте токен."
                )
        
        # Обновляем конфигурацию
        updated_config = await telegram_repo.update(config.id, config_data)
        
        if not updated_config:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Не удалось обновить конфигурацию"
            )
        
        return TelegramConfigResponse(
            id=updated_config.id,
            agent_id=updated_config.agent_id,
            user_id=updated_config.user_id,
            bot_token=updated_config.bot_token,
            chat_id=updated_config.chat_id,
            is_active=updated_config.is_active,
            created_at=updated_config.created_at,
            updated_at=updated_config.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка при обновлении Telegram конфигурации: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при обновлении конфигурации: {str(e)}"
        )


@router.delete("/{agent_id}/telegram-config")
async def delete_telegram_config(
    agent_id: int,
    current_user: User = Depends(require_active_subscription),
    db: AsyncSession = Depends(get_async_session)
):
    """
    Удаляет Telegram конфигурацию агента.
    Требует активную подписку.
    """
    try:
        # Проверяем доступ к агенту
        user_agent_repo = UserAgentRepository(db)
        user_agent = await user_agent_repo.get_by_user_and_agent(current_user.id, agent_id)
        
        if not user_agent or not user_agent.is_active:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Агент не найден или недоступен"
            )
        
        # Удаляем конфигурацию
        telegram_repo = TelegramConfigRepository(db)
        success = await telegram_repo.delete_by_user(agent_id, current_user.id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Telegram конфигурация не найдена"
            )
        
        return {"message": "Telegram конфигурация успешно удалена"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка при удалении Telegram конфигурации: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при удалении конфигурации: {str(e)}"
        )


@router.post("/{agent_id}/telegram-config/test")
async def test_telegram_config(
    agent_id: int,
    test_message: TelegramTestMessage,
    current_user: User = Depends(require_active_subscription),
    db: AsyncSession = Depends(get_async_session)
):
    """
    Отправляет тестовое сообщение в Telegram.
    Требует активную подписку.
    """
    try:
        # Проверяем доступ к агенту
        user_agent_repo = UserAgentRepository(db)
        user_agent = await user_agent_repo.get_by_user_and_agent(current_user.id, agent_id)
        
        if not user_agent or not user_agent.is_active:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Агент не найден или недоступен"
            )
        
        # Получаем конфигурацию
        telegram_repo = TelegramConfigRepository(db)
        config = await telegram_repo.get_by_agent_id(agent_id)
        
        if not config or not config.is_active:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Активная Telegram конфигурация не найдена"
            )
        
        # Форматируем тестовое сообщение
        formatted_message = f"""
🧪 <b>Тестовое сообщение</b>

{test_message.message}

---
<i>Отправлено из mara-ai для агента {agent_id}</i>
        """.strip()
        
        # Отправляем сообщение
        from src.agents.services.telegram_service import TelegramMessage
        
        message = TelegramMessage(
            chat_id=config.chat_id,
            text=formatted_message,
            parse_mode="HTML"
        )
        
        result = await telegram_service.send_message(config.bot_token, message)
        
        return {
            "success": True,
            "message": "Тестовое сообщение отправлено успешно",
            "telegram_message_id": result.get("result", {}).get("message_id")
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка при отправке тестового сообщения: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при отправке тестового сообщения: {str(e)}"
        )


@router.get("/telegram-configs", response_model=List[TelegramConfigResponse])
async def get_user_telegram_configs(
    current_user: User = Depends(require_active_subscription),
    db: AsyncSession = Depends(get_async_session)
):
    """
    Получает все Telegram конфигурации пользователя.
    Требует активную подписку.
    """
    try:
        telegram_repo = TelegramConfigRepository(db)
        configs = await telegram_repo.get_active_configs_by_user(current_user.id)
        
        return [
            TelegramConfigResponse(
                id=config.id,
                agent_id=config.agent_id,
                user_id=config.user_id,
                bot_token=config.bot_token,
                chat_id=config.chat_id,
                is_active=config.is_active,
                created_at=config.created_at,
                updated_at=config.updated_at
            )
            for config in configs
        ]
        
    except Exception as e:
        logger.error(f"Ошибка при получении Telegram конфигураций: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при получении конфигураций: {str(e)}"
        )
