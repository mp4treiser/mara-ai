import logging
import asyncio
import re
from typing import Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from src.core.orm.database import AsyncSessionLocal, SessionLocal
from src.agents.repositories.telegram_monitored_chat import TelegramMonitoredChatRepository
from src.agents.services.agent_service import AgentService
from src.agents.services.telegram_service import TelegramService, TelegramMessage
from src.core.celery_app import celery_app
from src.agents.models.telegram_monitored_chat import TelegramMonitoredChat
from src.agents.models.telegram_config import TelegramConfig
from src.agents.models.agent import Agent
from src.agents.services.vector_store import VectorStore
from src.agents.services.ollama_service import OllamaService
from src.core.config import settings
import requests

logger = logging.getLogger(__name__)

# Инициализируем сервисы
telegram_service = TelegramService()
agent_service = AgentService()


def _extract_alert_keywords(user_text: str) -> List[str]:
    """Извлекает ключевые слова из текста алерта"""
    keywords = []
    
    # Извлекаем название алерта из [Alerting] блока
    alerting_match = re.search(r'\[Alerting\](.+?)alert', user_text, re.IGNORECASE)
    if alerting_match:
        alert_name = alerting_match.group(1).strip()
        keywords.append(alert_name)
    
    logger.info(f"Извлечены ключевые слова из алерта: {keywords}")
    return keywords


@celery_app.task(bind=True, name="telegram_alert_tasks.process_telegram_alert_task")
def process_telegram_alert_task(
    self, 
    monitored_chat_id: int, 
    message_data: Dict[str, Any], 
    chat_id: str
) -> Dict[str, Any]:
    """
    Celery задача для обработки алерта из Telegram.
    Анализирует сообщение через агента и отправляет ответ.
    
    Args:
        monitored_chat_id: ID мониторинга чата
        message_data: Данные сообщения от Telegram
        chat_id: ID чата, откуда пришло сообщение
        
    Returns:
        Результат обработки алерта
    """
    task_id = self.request.id
    logger.info(f"Starting Telegram alert processing task {task_id} for monitored chat {monitored_chat_id}")
    
    try:
        # Используем синхронную версию для Celery
        result = _process_telegram_alert_sync(
            monitored_chat_id, message_data, chat_id
        )
        
        logger.info(f"Telegram alert processing task {task_id} completed successfully")
        return result
        
    except Exception as e:
        logger.error(f"Error in Telegram alert processing task {task_id}: {e}")
        return {
            "task_id": task_id,
            "success": False,
            "error": str(e),
            "monitored_chat_id": monitored_chat_id
        }


def _process_telegram_alert_sync(
    monitored_chat_id: int, 
    message_data: Dict[str, Any], 
    chat_id: str
) -> Dict[str, Any]:
    """Синхронная версия обработки алерта для Celery"""
    with SessionLocal() as db:
        try:
            monitored_chat = db.query(TelegramMonitoredChat).filter(
                TelegramMonitoredChat.id == monitored_chat_id
            ).first()
            
            if not monitored_chat or not monitored_chat.is_active:
                logger.warning(f"Monitored chat {monitored_chat_id} not found or inactive")
                return {
                    "success": False,
                    "error": "Мониторинг чата не найден или неактивен"
                }
            
            # Получаем Telegram конфигурацию
            telegram_config = db.query(TelegramConfig).filter(
                TelegramConfig.id == monitored_chat.telegram_config_id
            ).first()
            
            if not telegram_config or not telegram_config.is_active:
                logger.warning(f"Telegram config not found or inactive for monitored chat {monitored_chat_id}")
                return {
                    "success": False,
                    "error": "Telegram конфигурация не найдена или неактивна"
                }
            
            # Извлекаем текст сообщения
            message_text = message_data.get("text", "")
            if not message_text.strip():
                logger.info(f"No text in message from chat {chat_id}")
                return {
                    "success": False,
                    "error": "Сообщение не содержит текста"
                }
            
            # Формируем контекст для анализа
            alert_context = f"""
            АЛЕРТ ИЗ TELEGRAM:
            Чат: {monitored_chat.chat_title or chat_id}
            Тип чата: {monitored_chat.chat_type}
            Время: {message_data.get('date', 'Неизвестно')}
            Отправитель: {message_data.get('from', {}).get('username', 'Неизвестно')}
            
            СООБЩЕНИЕ:
            {message_text}
            
            Пожалуйста, проанализируй этот алерт и предоставь краткий анализ ситуации.
            """.strip()
            
            # Анализируем алерт через агента (полностью синхронно)
            try:
                # Получаем агента синхронно

                agent = db.query(Agent).filter(Agent.id == telegram_config.agent_id).first()
                
                if not agent:
                    analysis_text = "Агент не найден"
                else:
                    # Выполняем анализ через агента синхронно
                    analysis_result = _analyze_with_agent_sync_simple(
                        telegram_config.agent_id,
                        telegram_config.user_id,
                        alert_context
                    )
                    
                    if analysis_result and analysis_result.get("response"):
                        analysis_text = analysis_result["response"]
                    else:
                        analysis_text = "Не удалось проанализировать алерт через ИИ агента."
                    
            except Exception as e:
                logger.error(f"Error analyzing alert with agent: {e}")
                analysis_text = f"Ошибка при анализе алерта через ИИ: {str(e)}"
            
            # Формируем ответное сообщение с анализом ИИ
            response_message = f"""
            🚨 <b>АНАЛИЗ АЛЕРТА</b>
            
            📊 <b>Источник:</b> {monitored_chat.chat_title or chat_id}
            ⏰ <b>Время:</b> {message_data.get('date', 'Неизвестно')}
            👤 <b>Отправитель:</b> {message_data.get('from', {}).get('username', 'Неизвестно')}
            
            📝 <b>Исходное сообщение:</b>
            {message_text}
            
            🤖 <b>Анализ ИИ:</b>
            {analysis_text}
            
            ---
            <i>Автоматический анализ от mara-ai</i>
            """.strip()
            

            bot_token = telegram_config.bot_token
            target_chat_id = telegram_config.chat_id
            
            url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            data = {
                "chat_id": target_chat_id,
                "text": response_message,
                "parse_mode": "HTML"
            }
            
            logger.info(f"Sending response to chat {target_chat_id}")
            
            response = requests.post(url, json=data, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"Alert analysis sent successfully to chat {target_chat_id}")
                logger.info(f"Message ID: {result.get('result', {}).get('message_id')}")
                
                return {
                    "success": True,
                    "message": "Алерт проанализирован и ответ отправлен",
                    "monitored_chat_id": monitored_chat_id,
                    "source_chat_id": chat_id,
                    "target_chat_id": target_chat_id,
                    "telegram_message_id": result.get("result", {}).get("message_id")
                }
            else:
                error_text = response.text
                logger.error(f"Error sending alert analysis: {response.status_code} - {error_text}")
                return {
                    "success": False,
                    "error": f"Ошибка отправки анализа: {response.status_code} - {error_text}"
                }
            
        except Exception as e:
            logger.error(f"Error in alert processing: {e}")
            return {
                "success": False,
                "error": str(e)
            }


def _analyze_with_agent_sync_simple(
    agent_id: int,
    user_id: int,
    text: str
) -> Dict[str, Any]:
    """Анализирует текст через ИИ агента (полностью синхронная версия)"""
    try:
        # Создаем сервисы
        vector_store = VectorStore()
        ollama_service = OllamaService()
        
        # Создаем новую синхронную сессию для анализа агента
        with SessionLocal() as db:
            # Получаем агента

            agent = db.query(Agent).filter(Agent.id == agent_id).first()
            
            if not agent:
                return {"response": "Агент не найден"}
            
            # Выполняем поиск в векторной БД
            logger.info(f"Searching vector database for agent {agent_id}, user {user_id}")
            similar_docs = vector_store.search_similar(
                user_id=user_id,
                agent_id=agent_id,
                query=text,
                n_results=3
            )
            
            logger.info(f"Found {len(similar_docs)} similar documents")
            
            # Формируем контекст
            context = ""
            if similar_docs:
                context = "\n\n".join([doc.get("text", "") for doc in similar_docs])
                logger.info(f"Context length: {len(context)} characters")
                logger.info(f"First document preview: {similar_docs[0].get('text', '')[:200]}...")
            else:
                logger.warning("No similar documents found")
            
            # Генерируем ответ через LLM (используем тот же подход, что и на фронтенде)
            logger.info("Generating response with LLM")
            logger.info(f"Context preview: {context[:500]}...")
            logger.info(f"User text: {text[:200]}...")
            
            # Используем промпт агента, как на фронтенде
            response = ollama_service.generate_response(
                prompt=agent.prompt,
                context=context,
                user_text=text
            )
            
            logger.info(f"Generated response: {response[:100]}...")
            
            # Сохраняем лог
            from src.agents.models.agent_log import AgentLog
            agent_log = AgentLog(
                agent_id=agent_id,
                user_id=user_id,
                text_analyzed=text,
                response=response,
                processing_time=0.0,  # Будет обновлено позже
                text_length=len(text),
                documents_used=len(similar_docs)
            )
            db.add(agent_log)
            db.commit()
            
            return {"response": response}
            
    except Exception as e:
        logger.error(f"Error in agent analysis: {e}")
        return {"response": f"Ошибка анализа: {str(e)}"}


async def _analyze_with_agent_sync(
    agent_id: int,
    user_id: int,
    text: str
) -> Dict[str, Any]:
    """Анализирует текст через ИИ агента (синхронная версия)"""
    try:
        # Создаем новую асинхронную сессию для анализа агента
        async with AsyncSessionLocal() as async_db:
            analysis_result = await agent_service.analyze_text(
                agent_id=agent_id,
                user_id=user_id,
                text=text,
                db_session=async_db
            )
            return analysis_result
    except Exception as e:
        logger.error(f"Error in agent analysis: {e}")
        return {"response": f"Ошибка анализа: {str(e)}"}


async def _analyze_with_agent(
    agent_id: int,
    user_id: int,
    text: str
) -> Dict[str, Any]:
    """Анализирует текст через ИИ агента"""
    try:
        async with AsyncSessionLocal() as db:
            analysis_result = await agent_service.analyze_text(
                agent_id=agent_id,
                user_id=user_id,
                text=text,
                db_session=db
            )
            return analysis_result
    except Exception as e:
        logger.error(f"Error in agent analysis: {e}")
        return {"response": f"Ошибка анализа: {str(e)}"}


async def _process_telegram_alert_async(
    monitored_chat_id: int, 
    message_data: Dict[str, Any], 
    chat_id: str
) -> Dict[str, Any]:
    """Асинхронная часть обработки алерта"""
    async with AsyncSessionLocal() as db:
        try:
            # Получаем информацию о мониторинге
            monitoring_repo = TelegramMonitoredChatRepository(db)
            monitored_chat = await monitoring_repo.get_by_id(monitored_chat_id)
            
            if not monitored_chat or not monitored_chat.is_active:
                logger.warning(f"Monitored chat {monitored_chat_id} not found or inactive")
                return {
                    "success": False,
                    "error": "Мониторинг чата не найден или неактивен"
                }
            
            # Получаем Telegram конфигурацию
            telegram_config = monitored_chat.telegram_config
            if not telegram_config or not telegram_config.is_active:
                logger.warning(f"Telegram config not found or inactive for monitored chat {monitored_chat_id}")
                return {
                    "success": False,
                    "error": "Telegram конфигурация не найдена или неактивна"
                }
            
            # Извлекаем текст сообщения
            message_text = message_data.get("text", "")
            if not message_text.strip():
                logger.info(f"No text in message from chat {chat_id}")
                return {
                    "success": False,
                    "error": "Сообщение не содержит текста"
                }
            
            # Формируем контекст для анализа
            alert_context = f"""
            АЛЕРТ ИЗ TELEGRAM:
            Чат: {monitored_chat.chat_title or chat_id}
            Тип чата: {monitored_chat.chat_type}
            Время: {message_data.get('date', 'Неизвестно')}
            Отправитель: {message_data.get('from', {}).get('username', 'Неизвестно')}
            
            СООБЩЕНИЕ:
            {message_text}
            
            Пожалуйста, проанализируй этот алерт и предоставь краткий анализ ситуации.
            """.strip()
            
            # Анализируем алерт через агента
            try:
                analysis_result = await agent_service.analyze_text(
                    agent_id=telegram_config.agent_id,
                    user_id=telegram_config.user_id,
                    text=alert_context,
                    db_session=db
                )
                
                if not analysis_result or not analysis_result.get("response"):
                    logger.warning(f"No analysis result for alert from chat {chat_id}")
                    return {
                        "success": False,
                        "error": "Не удалось проанализировать алерт"
                    }
                
                analysis_text = analysis_result["response"]
                
            except Exception as e:
                logger.error(f"Error analyzing alert: {e}")
                analysis_text = f"Ошибка при анализе алерта: {str(e)}"
            
            # Формируем ответное сообщение
            response_message = f"""
            🚨 <b>АНАЛИЗ АЛЕРТА</b>
            
            📊 <b>Источник:</b> {monitored_chat.chat_title or chat_id}
            ⏰ <b>Время:</b> {message_data.get('date', 'Неизвестно')}
            👤 <b>Отправитель:</b> {message_data.get('from', {}).get('username', 'Неизвестно')}
            
            📝 <b>Исходное сообщение:</b>
            {message_text}
            
            🤖 <b>Анализ ИИ:</b>
            {analysis_text}
            
            ---
            <i>Автоматический анализ от mara-ai</i>
            """.strip()
            
            # Отправляем ответ в чат для уведомлений
            try:
                message = TelegramMessage(
                    chat_id=telegram_config.chat_id,
                    text=response_message,
                    parse_mode="HTML"
                )
                
                result = await telegram_service.send_message(telegram_config.bot_token, message)
                
                logger.info(f"Alert analysis sent successfully to chat {telegram_config.chat_id}")
                
                return {
                    "success": True,
                    "message": "Алерт проанализирован и ответ отправлен",
                    "monitored_chat_id": monitored_chat_id,
                    "source_chat_id": chat_id,
                    "target_chat_id": telegram_config.chat_id,
                    "telegram_message_id": result.get("result", {}).get("message_id"),
                    "analysis_length": len(analysis_text)
                }
                
            except Exception as e:
                logger.error(f"Error sending alert analysis: {e}")
                return {
                    "success": False,
                    "error": f"Ошибка отправки анализа: {str(e)}"
                }
            
        except Exception as e:
            logger.error(f"Error in alert processing: {e}")
            return {
                "success": False,
                "error": str(e)
            }


@celery_app.task(bind=True, name="test_telegram_monitoring")
def test_telegram_monitoring_task(
    self, 
    monitored_chat_id: int, 
    test_message: str
) -> Dict[str, Any]:
    """
    Celery задача для тестирования мониторинга Telegram.
    Отправляет тестовое сообщение в чат для уведомлений.
    
    Args:
        monitored_chat_id: ID мониторинга чата
        test_message: Тестовое сообщение
        
    Returns:
        Результат тестирования
    """
    task_id = self.request.id
    logger.info(f"Starting Telegram monitoring test task {task_id}")
    
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            # Выполняем асинхронную задачу
            result = loop.run_until_complete(_test_telegram_monitoring_async(
                monitored_chat_id, test_message
            ))
        finally:
            loop.close()
        
        logger.info(f"Telegram monitoring test task {task_id} completed")
        return result
        
    except Exception as e:
        logger.error(f"Error in Telegram monitoring test task {task_id}: {e}")
        return {
            "task_id": task_id,
            "success": False,
            "error": str(e)
        }


async def _test_telegram_monitoring_async(
    monitored_chat_id: int, 
    test_message: str
) -> Dict[str, Any]:
    """Асинхронная часть тестирования мониторинга"""
    async with AsyncSessionLocal() as db:
        try:
            # Получаем информацию о мониторинге
            monitoring_repo = TelegramMonitoredChatRepository(db)
            monitored_chat = await monitoring_repo.get_by_id(monitored_chat_id)
            
            if not monitored_chat:
                return {
                    "success": False,
                    "error": "Мониторинг чата не найден"
                }
            
            # Получаем Telegram конфигурацию
            telegram_config = monitored_chat.telegram_config
            if not telegram_config:
                return {
                    "success": False,
                    "error": "Telegram конфигурация не найдена"
                }
            
            # Формируем тестовое сообщение
            test_response = f"""
            🧪 <b>ТЕСТ МОНИТОРИНГА</b>
            
            📊 <b>Мониторинг чата:</b> {monitored_chat.chat_title or monitored_chat.chat_id}
            🔍 <b>Тип чата:</b> {monitored_chat.chat_type}
            🏷️ <b>Ключевые слова:</b> {', '.join(monitored_chat.keywords) if monitored_chat.keywords else 'Не заданы'}
            
            📝 <b>Тестовое сообщение:</b>
            {test_message}
            
            ✅ <b>Статус:</b> Мониторинг работает корректно!
            
            ---
            <i>Тестовое сообщение от mara-ai</i>
            """.strip()
            
            # Отправляем тестовое сообщение
            message = TelegramMessage(
                chat_id=telegram_config.chat_id,
                text=test_response,
                parse_mode="HTML"
            )
            
            result = await telegram_service.send_message(telegram_config.bot_token, message)
            
            return {
                "success": True,
                "message": "Тестовое сообщение отправлено успешно",
                "monitored_chat_id": monitored_chat_id,
                "telegram_message_id": result.get("result", {}).get("message_id")
            }
            
        except Exception as e:
            logger.error(f"Error in monitoring test: {e}")
            return {
                "success": False,
                "error": str(e)
            }
