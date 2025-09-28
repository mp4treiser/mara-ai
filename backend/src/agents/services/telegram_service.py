import logging
import httpx
from typing import Optional, Dict, Any
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class TelegramMessage(BaseModel):
    chat_id: str
    text: str
    parse_mode: str = "HTML"
    disable_web_page_preview: bool = False


class TelegramService:
    """Сервис для работы с Telegram Bot API"""
    
    def __init__(self):
        self.base_url = "https://api.telegram.org/bot"
        self.timeout = 30  # Таймаут для запросов в секундах
    
    async def send_message(self, bot_token: str, message: TelegramMessage) -> Dict[str, Any]:
        """
        Отправляет сообщение через Telegram Bot API
        
        Args:
            bot_token: Токен бота
            message: Объект сообщения
            
        Returns:
            Ответ от Telegram API
            
        Raises:
            Exception: При ошибке отправки сообщения
        """
        try:
            url = f"{self.base_url}{bot_token}/sendMessage"
            
            payload = {
                "chat_id": message.chat_id,
                "text": message.text,
                "parse_mode": message.parse_mode,
                "disable_web_page_preview": message.disable_web_page_preview
            }
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(url, json=payload)
                response.raise_for_status()
                
                result = response.json()
                
                if result.get("ok"):
                    logger.info(f"Сообщение успешно отправлено в чат {message.chat_id}")
                    return result
                else:
                    error_msg = result.get("description", "Неизвестная ошибка")
                    logger.error(f"Ошибка отправки сообщения в Telegram: {error_msg}")
                    raise Exception(f"Telegram API error: {error_msg}")
                    
        except httpx.HTTPStatusError as e:
            error_msg = f"HTTP error {e.response.status_code}: {e.response.text}"
            logger.error(f"HTTP ошибка при отправке в Telegram: {error_msg}")
            raise Exception(error_msg)
            
        except httpx.RequestError as e:
            error_msg = f"Network error: {str(e)}"
            logger.error(f"Ошибка сети при отправке в Telegram: {error_msg}")
            raise Exception(error_msg)
            
        except Exception as e:
            logger.error(f"Неожиданная ошибка при отправке в Telegram: {str(e)}")
            raise
    
    async def get_bot_info(self, bot_token: str) -> Dict[str, Any]:
        """
        Получает информацию о боте
        
        Args:
            bot_token: Токен бота
            
        Returns:
            Информация о боте
            
        Raises:
            Exception: При ошибке получения информации
        """
        try:
            url = f"{self.base_url}{bot_token}/getMe"
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url)
                response.raise_for_status()
                
                result = response.json()
                
                if result.get("ok"):
                    logger.info(f"Информация о боте получена успешно")
                    return result.get("result", {})
                else:
                    error_msg = result.get("description", "Неизвестная ошибка")
                    logger.error(f"Ошибка получения информации о боте: {error_msg}")
                    raise Exception(f"Telegram API error: {error_msg}")
                    
        except httpx.HTTPStatusError as e:
            error_msg = f"HTTP error {e.response.status_code}: {e.response.text}"
            logger.error(f"HTTP ошибка при получении информации о боте: {error_msg}")
            raise Exception(error_msg)
            
        except httpx.RequestError as e:
            error_msg = f"Network error: {str(e)}"
            logger.error(f"Ошибка сети при получении информации о боте: {error_msg}")
            raise Exception(error_msg)
            
        except Exception as e:
            logger.error(f"Неожиданная ошибка при получении информации о боте: {str(e)}")
            raise
    
    async def test_bot_connection(self, bot_token: str) -> bool:
        """
        Тестирует подключение к боту
        
        Args:
            bot_token: Токен бота
            
        Returns:
            True если подключение успешно, False в противном случае
        """
        try:
            await self.get_bot_info(bot_token)
            return True
        except Exception as e:
            logger.warning(f"Не удалось подключиться к боту: {str(e)}")
            return False
    
    def format_agent_response(self, agent_name: str, query: str, response: str) -> str:
        """
        Форматирует ответ агента для отправки в Telegram
        
        Args:
            agent_name: Название агента
            query: Запрос пользователя
            response: Ответ агента
            
        Returns:
            Отформатированное сообщение
        """
        # Ограничиваем длину сообщения (Telegram имеет лимит 4096 символов)
        max_length = 3500  # Оставляем запас для форматирования
        
        if len(response) > max_length:
            response = response[:max_length] + "..."
        
        # Форматируем сообщение с HTML разметкой
        formatted_message = f"""
🤖 <b>{agent_name}</b>

📝 <b>Запрос:</b>
{query}

💬 <b>Ответ:</b>
{response}

---
<i>Отправлено через mara-ai</i>
        """.strip()
        
        return formatted_message
    
    def validate_bot_token(self, bot_token: str) -> bool:
        """
        Валидирует формат токена бота
        
        Args:
            bot_token: Токен для проверки
            
        Returns:
            True если токен валиден, False в противном случае
        """
        if not bot_token:
            return False
        
        # Токен должен содержать двоеточие и быть достаточно длинным
        if ':' not in bot_token or len(bot_token) < 20:
            return False
        
        # Первая часть должна быть числом
        try:
            bot_id = bot_token.split(':')[0]
            int(bot_id)
            return True
        except (ValueError, IndexError):
            return False
    
    def validate_chat_id(self, chat_id: str) -> bool:
        """
        Валидирует формат ID чата
        
        Args:
            chat_id: ID чата для проверки
            
        Returns:
            True если ID валиден, False в противном случае
        """
        if not chat_id:
            return False
        
        # Для личных чатов: только цифры (возможно с минусом)
        if chat_id.replace('-', '').replace('_', '').isdigit():
            return True
        
        # Для каналов и групп: начинается с @ или содержит @
        if chat_id.startswith('@') or '@' in chat_id:
            return True
        
        return False
    
    async def set_webhook(self, bot_token: str, webhook_url: str) -> Dict[str, Any]:
        """
        Устанавливает webhook для Telegram бота
        
        Args:
            bot_token: Токен бота
            webhook_url: URL для webhook
            
        Returns:
            Ответ от Telegram API
        """
        try:
            url = f"{self.base_url}{bot_token}/setWebhook"
            
            payload = {
                "url": webhook_url
            }
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(url, json=payload)
                response.raise_for_status()
                
                result = response.json()
                logger.info(f"Webhook установлен для бота: {webhook_url}")
                return result
                
        except Exception as e:
            logger.error(f"Ошибка при установке webhook: {e}")
            raise
    
    async def get_webhook_info(self, bot_token: str) -> Dict[str, Any]:
        """
        Получает информацию о текущем webhook бота
        
        Args:
            bot_token: Токен бота
            
        Returns:
            Информация о webhook
        """
        try:
            url = f"{self.base_url}{bot_token}/getWebhookInfo"
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url)
                response.raise_for_status()
                
                result = response.json()
                logger.info(f"Получена информация о webhook для бота")
                return result
                
        except Exception as e:
            logger.error(f"Ошибка при получении информации о webhook: {e}")
            raise
    
    async def delete_webhook(self, bot_token: str) -> Dict[str, Any]:
        """
        Удаляет webhook для Telegram бота
        
        Args:
            bot_token: Токен бота
            
        Returns:
            Ответ от Telegram API
        """
        try:
            url = f"{self.base_url}{bot_token}/deleteWebhook"
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(url)
                response.raise_for_status()
                
                result = response.json()
                logger.info(f"Webhook удален для бота")
                return result
                
        except Exception as e:
            logger.error(f"Ошибка при удалении webhook: {e}")
            raise
