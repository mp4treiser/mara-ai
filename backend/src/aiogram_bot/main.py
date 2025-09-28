"""
Основной файл для запуска aiogram бота
"""
import asyncio
import logging
import signal
import sys
from typing import Dict, Set
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import traceback
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.orm.database import AsyncSessionLocal
from src.core.orm.database import get_async_session
from src.agents.repositories.telegram_monitored_chat import TelegramMonitoredChatRepository
from src.agents.repositories.telegram_config import TelegramConfigRepository
from src.tasks.telegram_alert_tasks import process_telegram_alert_task
from src.core.celery_app import celery_app
import json

# Простая функция для получения сессии
async def get_db_session():
    """Получает сессию базы данных"""
    async with AsyncSessionLocal() as session:
        return session

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TelegramBotManager:
    """Менеджер для управления Telegram ботами"""
    
    def __init__(self):
        self.bots: Dict[str, Bot] = {}
        self.dispatchers: Dict[str, Dispatcher] = {}
        self.monitored_chats: Dict[str, Set[str]] = {}
        self.running = False
        self.tasks = []
    
    async def start_bot(self, bot_token: str) -> bool:
        """Запускает бота для мониторинга"""
        try:
            if bot_token in self.bots:
                logger.info(f"Bot {bot_token[:10]}... already running")
                return True
            
            # Создаем бота и диспетчер
            bot = Bot(token=bot_token)
            storage = MemoryStorage()
            dp = Dispatcher(storage=storage)
            
            # Регистрируем обработчики
            self._register_handlers(dp, bot_token)
            
            # Сохраняем экземпляры
            self.bots[bot_token] = bot
            self.dispatchers[bot_token] = dp
            self.monitored_chats[bot_token] = set()
            
            # Запускаем polling
            task = asyncio.create_task(self._start_polling(bot, dp))
            self.tasks.append(task)
            
            logger.info(f"Bot {bot_token[:10]}... started successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error starting bot {bot_token[:10]}...: {e}")
            return False
    
    async def stop_bot(self, bot_token: str) -> bool:
        """Останавливает бота"""
        try:
            if bot_token not in self.bots:
                logger.warning(f"Bot {bot_token[:10]}... not running")
                return True
            
            # Останавливаем бота
            bot = self.bots[bot_token]
            await bot.session.close()
            
            # Удаляем из словарей
            del self.bots[bot_token]
            del self.dispatchers[bot_token]
            if bot_token in self.monitored_chats:
                del self.monitored_chats[bot_token]
            
            logger.info(f"Bot {bot_token[:10]}... stopped successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error stopping bot {bot_token[:10]}...: {e}")
            return False
    
    async def update_monitored_chats(self, bot_token: str) -> None:
        """Обновляет список мониторимых чатов для бота"""
        try:
            # Получаем сессию базы данных
            db = await get_db_session()
            try:
                # Получаем все активные мониторинги для этого бота
                config_repo = TelegramConfigRepository(db)
                monitoring_repo = TelegramMonitoredChatRepository(db)
                
                # Находим конфигурацию по токену
                config = await config_repo.get_by_bot_token(bot_token)
                if not config:
                    logger.warning(f"No config found for bot {bot_token[:10]}...")
                    return
                
                # Получаем мониторинги
                monitored_chats = await monitoring_repo.get_by_config_id(config.id)
                logger.info(f"Found {len(monitored_chats)} monitored chats for config {config.id}")
                
                # Обновляем список только активных чатов
                chat_ids = {chat.chat_id for chat in monitored_chats if chat.is_active}
                self.monitored_chats[bot_token] = chat_ids
                
                logger.info(f"Updated monitored chats for bot {bot_token[:10]}...: {len(chat_ids)} chats")
                logger.info(f"Chat IDs: {list(chat_ids)}")
                
            finally:
                await db.close()
                
        except Exception as e:
            logger.error(f"Error updating monitored chats for bot {bot_token[:10]}...: {e}")
    
    def _register_handlers(self, dp: Dispatcher, bot_token: str) -> None:
        """Регистрирует обработчики сообщений"""
        
        # Добавляем обработчик всех обновлений для отладки
        @dp.update()
        async def handle_update(update):
            """Обработчик всех обновлений для отладки"""
            logger.info(f"Received update: {update}")
            logger.info(f"Update type: {update.event_type}")
            if hasattr(update, 'message') and update.message:
                logger.info(f"Message in update: {update.message}")
                logger.info(f"Message text: {update.message.text}")
                logger.info(f"Message chat: {update.message.chat}")
        
        @dp.message()
        async def handle_message(message: Message):
            """Обработчик всех сообщений"""
            try:
                chat_id = str(message.chat.id)
                bot_token = message.bot.token
                
                # Логируем все сообщения для отладки
                logger.info(f"Received message in chat {chat_id} from bot {bot_token[:10]}...")
                logger.info(f"Message type: {message.content_type}")
                logger.info(f"Message text: {message.text}")
                logger.info(f"Chat type: {message.chat.type}")
                
                # Проверяем, мониторится ли этот чат
                if bot_token not in self.monitored_chats:
                    logger.debug(f"Bot {bot_token[:10]}... not in monitored bots")
                    return
                
                if chat_id not in self.monitored_chats[bot_token]:
                    logger.debug(f"Chat {chat_id} not monitored by bot {bot_token[:10]}...")
                    return
                
                logger.info(f"Chat {chat_id} is monitored by bot {bot_token[:10]}...")
                
                # Получаем информацию о мониторинге
                db = await get_db_session()
                try:
                    monitoring_repo = TelegramMonitoredChatRepository(db)
                    monitored_chats = await monitoring_repo.get_by_chat_id(chat_id)
                    
                    logger.info(f"Found {len(monitored_chats)} monitored chat configs for chat {chat_id}")
                    
                    for monitored_chat in monitored_chats:
                        if not monitored_chat.is_active:
                            logger.debug(f"Monitored chat {monitored_chat.id} is not active")
                            continue
                        
                        logger.info(f"Processing monitored chat {monitored_chat.id} with keywords: {monitored_chat.keywords}")
                        
                        # Проверяем ключевые слова
                        if monitored_chat.keywords:
                            try:
                                keywords = json.loads(monitored_chat.keywords) if isinstance(monitored_chat.keywords, str) else monitored_chat.keywords
                                message_text = message.text or ""
                                
                                logger.info(f"Checking keywords {keywords} in message: '{message_text}'")
                                
                                if keywords and not any(keyword.lower() in message_text.lower() for keyword in keywords):
                                    logger.debug(f"Message doesn't contain keywords: {keywords}")
                                    continue
                                    
                                logger.info(f"Message contains keywords! Processing...")
                                    
                            except (json.JSONDecodeError, TypeError) as e:
                                logger.error(f"Error parsing keywords: {e}")
                                # Если keywords невалидный JSON, пропускаем фильтрацию
                                pass
                        else:
                            logger.info("No keywords filter, processing all messages")
                        
                        # Отправляем задачу в Celery для анализа через Ollama
                        try:
                            logger.info(f"Processing alert for monitored_chat_id={monitored_chat.id}, chat_id={chat_id}")
                            
                            # Получаем Telegram конфигурацию
                            telegram_config = monitored_chat.telegram_config
                            if not telegram_config or not telegram_config.is_active:
                                logger.warning(f"Telegram config not found or inactive for monitored chat {monitored_chat.id}")
                                return
                            
                            # Формируем данные для задачи
                            message_text = message.text or ""
                            message_data = {
                                "text": message_text,
                                "date": message.date.isoformat() if message.date else None,
                                "from": {
                                    "username": message.from_user.username if message.from_user else None,
                                    "id": message.from_user.id if message.from_user else None
                                },
                                "chat_title": monitored_chat.chat_title,
                                "chat_type": monitored_chat.chat_type
                            }
                            
                            logger.info(f"Sending alert task to Celery for analysis")
                            
                            # Отправляем задачу в Celery с правильными параметрами

                            logger.info(f"Calling Celery task with params: monitored_chat_id={monitored_chat.id}, chat_id={chat_id}")
                            
                            try:
                                # Используем правильное имя задачи из Celery

                                task = celery_app.send_task(
                                    'telegram_alert_tasks.process_telegram_alert_task',
                                    args=[monitored_chat.id, message_data, chat_id]
                                )
                                
                                logger.info(f"Alert task sent to Celery with ID: {task.id}")
                                logger.info(f"Task state: {task.state}")
                                
                            except Exception as celery_error:
                                logger.error(f"Error sending task to Celery: {celery_error}")
                                logger.error(f"Celery error traceback: {traceback.format_exc()}")
                            
                        except Exception as e:
                            logger.error(f"Error processing alert: {e}")
                            logger.error(f"Traceback: {traceback.format_exc()}")
                    
                finally:
                    await db.close()
                    
            except Exception as e:
                logger.error(f"Error handling message: {e}")

                logger.error(f"Traceback: {traceback.format_exc()}")
    
    async def _start_polling(self, bot: Bot, dp: Dispatcher) -> None:
        """Запускает polling для бота"""
        try:
            await dp.start_polling(bot)
        except Exception as e:
            logger.error(f"Error in polling: {e}")
    
    async def start_all_bots(self) -> None:
        """Запускает всех активных ботов"""
        try:
            # Получаем сессию базы данных
            db = await get_db_session()
            try:
                config_repo = TelegramConfigRepository(db)
                
                # Получаем все активные конфигурации
                configs = await config_repo.get_all_active_configs()
                
                for config in configs:
                    if config.is_active:
                        await self.start_bot(config.bot_token)
                        await self.update_monitored_chats(config.bot_token)
                
                self.running = True
                logger.info(f"Started {len(self.bots)} bots")
                
            finally:
                await db.close()
                
        except Exception as e:
            logger.error(f"Error starting bots: {e}")
    
    async def stop_all_bots(self) -> None:
        """Останавливает всех ботов"""
        try:
            for bot_token in list(self.bots.keys()):
                await self.stop_bot(bot_token)
            
            # Отменяем все задачи
            for task in self.tasks:
                task.cancel()
            
            self.tasks.clear()
            self.running = False
            logger.info("All bots stopped")
            
        except Exception as e:
            logger.error(f"Error stopping bots: {e}")


# Глобальный экземпляр менеджера
bot_manager = TelegramBotManager()

# Создаем FastAPI приложение для управления ботами
app = FastAPI(title="Aiogram Bot Manager", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/start-bot")
async def start_bot_endpoint(request: dict):
    """API endpoint для запуска бота"""
    try:
        bot_token = request.get("bot_token")
        if not bot_token:
            raise HTTPException(status_code=400, detail="bot_token is required")
        
        success = await bot_manager.start_bot(bot_token)
        if success:
            return {"success": True, "message": "Bot started successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to start bot")
            
    except Exception as e:
        logger.error(f"Error in start_bot_endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/stop-bot")
async def stop_bot_endpoint(request: dict):
    """API endpoint для остановки бота"""
    try:
        bot_token = request.get("bot_token")
        if not bot_token:
            raise HTTPException(status_code=400, detail="bot_token is required")
        
        success = await bot_manager.stop_bot(bot_token)
        if success:
            return {"success": True, "message": "Bot stopped successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to stop bot")
            
    except Exception as e:
        logger.error(f"Error in stop_bot_endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/update-monitored-chats")
async def update_monitored_chats_endpoint(request: dict):
    """API endpoint для обновления мониторимых чатов"""
    try:
        bot_token = request.get("bot_token")
        if not bot_token:
            raise HTTPException(status_code=400, detail="bot_token is required")
        
        await bot_manager.update_monitored_chats(bot_token)
        return {"success": True, "message": "Monitored chats updated successfully"}
            
    except Exception as e:
        logger.error(f"Error in update_monitored_chats_endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/start-all-bots")
async def start_all_bots_endpoint():
    """API endpoint для запуска всех активных ботов"""
    try:
        await bot_manager.start_all_bots()
        return {"success": True, "message": f"Started {len(bot_manager.bots)} bots"}
    except Exception as e:
        logger.error(f"Error in start_all_bots_endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "running_bots": len(bot_manager.bots), "monitored_chats": sum(len(chats) for chats in bot_manager.monitored_chats.values())}

async def main():
    """Основная функция"""
    logger.info("Starting Telegram Bot Manager...")
    
    try:
        # Запускаем всех активных ботов из БД
        logger.info("Starting all active bots from database...")
        await bot_manager.start_all_bots()
        
        # Запускаем FastAPI сервер
        config = uvicorn.Config(app, host="0.0.0.0", port=8001, log_level="info")
        server = uvicorn.Server(config)
        
        # Запускаем сервер в отдельной задаче
        server_task = asyncio.create_task(server.serve())
        
        # Обработчик сигналов для корректного завершения
        def signal_handler(signum, frame):
            logger.info(f"Received signal {signum}, shutting down...")
            asyncio.create_task(bot_manager.stop_all_bots())
            server_task.cancel()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        # Ждем завершения сервера
        await server_task
            
    except Exception as e:
        logger.error(f"Error in main: {e}")
        await bot_manager.stop_all_bots()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
