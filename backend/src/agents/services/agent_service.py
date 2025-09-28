import time
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path
from sqlalchemy.ext.asyncio import AsyncSession

from .vector_store import VectorStore
from .ollama_service import OllamaService
from .document_processor import DocumentProcessor
from .telegram_service import TelegramService, TelegramMessage
from ..models.agent import Agent
from ..models.document import Document
from ..models.agent_log import AgentLog
from ..repositories.agent import AgentRepository

logger = logging.getLogger(__name__)


class AgentService:
    """Основной сервис для работы с агентами"""
    
    def __init__(self):
        self.vector_store = VectorStore()
        self.ollama_service = OllamaService()
        self.document_processor = DocumentProcessor()
        self.telegram_service = TelegramService()
    
    async def analyze_text(self, agent_id: int, user_id: int, text: str, db_session) -> Dict[str, Any]:
        """Анализирует текст с помощью агента"""
        start_time = time.time()
        
        try:
            # Валидация входных параметров
            if not text or not text.strip():
                return {
                    "success": False,
                    "error_message": "Текст для анализа не может быть пустым",
                    "processing_time": 0.0,
                    "documents_used": 0
                }
            
            # Получаем агента
            agent = await self._get_agent(agent_id, db_session)
            if not agent:
                return {
                    "success": False,
                    "error_message": "Агент не найден",
                    "processing_time": time.time() - start_time,
                    "documents_used": 0
                }
            
            # Проверяем, что пользователь имеет доступ к агенту
            from ..repositories.user_agent import UserAgentRepository
            user_agent_repo = UserAgentRepository(db_session)
            user_agent = await user_agent_repo.get_by_user_and_agent(user_id, agent_id)
            if not user_agent or not user_agent.is_active:
                logger.warning(f"Пользователь {user_id} пытается использовать недоступный агент {agent_id}")
                return {
                    "success": False,
                    "error_message": "Нет доступа к агенту",
                    "processing_time": time.time() - start_time,
                    "documents_used": 0
                }
            
            # Проверяем активность агента
            if not agent.is_active:
                return {
                    "success": False,
                    "error_message": "Агент неактивен",
                    "processing_time": time.time() - start_time,
                    "documents_used": 0
                }
            
            # Проверяем промпт агента
            if not agent.prompt or not agent.prompt.strip():
                return {
                    "success": False,
                    "error_message": "Промпт агента не настроен",
                    "processing_time": time.time() - start_time,
                    "documents_used": 0
                }
            
            # Ищем релевантные документы в векторной БД
            try:
                logger.info(f"Поиск документов для агента {agent_id}, пользователя {user_id}, запрос: '{text[:100]}...'")
                context_docs = self.vector_store.search_similar(user_id, agent_id, text, n_results=3)
                logger.info(f"Найдено {len(context_docs)} релевантных документов для агента {agent_id}")
                
                # Логируем найденные документы
                for i, doc in enumerate(context_docs):
                    logger.info(f"Документ {i+1}: {doc.get('filename', 'unknown')} - {doc.get('text', '')[:100]}...")
                    
            except Exception as e:
                logger.error(f"Ошибка при поиске документов для агента {agent_id}, пользователя {user_id}: {e}")
                # Возвращаем ошибку вместо пустого контекста для критических случаев
                return {
                    "success": False,
                    "error_message": "Ошибка при поиске документов в базе знаний",
                    "processing_time": time.time() - start_time,
                    "documents_used": 0
                }
            
            # Формируем контекст из документов
            context = self._build_context(context_docs)
            
            # Генерируем ответ через Ollama
            try:
                response = self.ollama_service.generate_response(
                    prompt=agent.prompt,
                    context=context,
                    user_text=text
                )
                
                # Проверяем, что получили валидный ответ
                if not response or not response.strip():
                    response = "Извините, не удалось сгенерировать ответ. Попробуйте переформулировать вопрос."
                    
            except Exception as e:
                logger.error(f"Ошибка при генерации ответа через Ollama: {e}")
                response = f"Произошла ошибка при генерации ответа: {str(e)}"
            
            # Вычисляем время обработки
            processing_time = time.time() - start_time
            
            # Сохраняем лог
            try:
                log = AgentLog(
                    agent_id=agent_id,
                    user_id=user_id,
                    text_analyzed=text,
                    response=response,
                    processing_time=processing_time,
                    text_length=len(text),
                    documents_used=len(context_docs)
                )
                
                db_session.add(log)
                await db_session.commit()
            except Exception as e:
                logger.error(f"Ошибка при сохранении лога: {e}")
                # Не прерываем выполнение, если не удалось сохранить лог
            
            return {
                "success": True,
                "agent_id": agent_id,
                "response": response,
                "processing_time": processing_time,
                "documents_used": len(context_docs)
            }
            
        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"Критическая ошибка при анализе текста агентом {agent_id}: {e}")
            
            return {
                "success": False,
                "error_message": f"Критическая ошибка: {str(e)}",
                "processing_time": processing_time,
                "documents_used": 0
            }
    
    def _build_context(self, context_docs: List[Dict[str, Any]]) -> str:
        """Строит контекст из найденных документов"""
        if not context_docs:
            return ""
        
        context_parts = []
        for doc in context_docs:
            filename = doc.get('metadata', {}).get('filename', 'Unknown')
            text = doc.get('text', '')
            context_parts.append(f"Документ: {filename}\n{text[:500]}...")
        
        return "\n\n".join(context_parts)
    
    async def _get_agent(self, agent_id: int, db_session: AsyncSession) -> Optional[Agent]:
        """Получает агента из БД"""
        try:
            repo = AgentRepository(db_session)
            return await repo.get_by_id(agent_id)
        except Exception as e:
            logger.error(f"Ошибка при получении агента {agent_id}: {e}")
            return None
    
    async def create_agent(self, agent_data, user_id: int, db_session: AsyncSession) -> Optional[Agent]:
        """Создает нового агента"""
        try:
            repo = AgentRepository(db_session)
            return await repo.create(agent_data, user_id)
        except Exception as e:
            logger.error(f"Ошибка при создании агента: {e}")
            return None
    
    async def get_all_agents(self, db_session: AsyncSession) -> List[Agent]:
        """Получает всех агентов"""
        try:
            repo = AgentRepository(db_session)
            return await repo.get_all()
        except Exception as e:
            logger.error(f"Ошибка при получении списка агентов: {e}")
            return []
    
    async def update_agent(self, agent_id: int, agent_data, db_session: AsyncSession) -> Optional[Agent]:
        """Обновляет агента"""
        try:
            repo = AgentRepository(db_session)
            return await repo.update(agent_id, agent_data)
        except Exception as e:
            logger.error(f"Ошибка при обновлении агента {agent_id}: {e}")
            return None
    
    async def delete_agent(self, agent_id: int, db_session: AsyncSession) -> bool:
        """Удаляет агента"""
        try:
            repo = AgentRepository(db_session)
            return await repo.delete(agent_id)
        except Exception as e:
            logger.error(f"Ошибка при удалении агента {agent_id}: {e}")
            return False
    
    async def process_document(self, agent_id: int, user_id: int, file_path: str, 
                             filename: str, file_type: str, db_session) -> bool:
        """Обрабатывает загруженный документ"""
        try:
            # Извлекаем текст из документа
            text = self.document_processor.extract_text(file_path, file_type)
            
            if not text:
                logger.warning(f"Не удалось извлечь текст из документа {filename}")
                return False
            
            # Добавляем в векторную БД
            doc_data = {
                'id': f"temp_{filename}",
                'text': text,
                'filename': filename,
                'file_type': file_type,
                'uploaded_at': time.time()
            }
            
            success = self.vector_store.add_documents(user_id, agent_id, [doc_data])
            
            if success:
                logger.info(f"Документ {filename} успешно обработан для агента {agent_id}")
                return True
            else:
                logger.error(f"Ошибка при добавлении документа {filename} в векторную БД")
                return False
                
        except Exception as e:
            logger.error(f"Ошибка при обработке документа {filename}: {e}")
            return False
    
    def test_ollama_connection(self) -> bool:
        """Тестирует подключение к Ollama"""
        return self.ollama_service.test_connection()
    
    def get_agent_stats(self, agent_id: int, user_id: int) -> Dict[str, Any]:
        """Получает статистику агента"""
        try:
            # Получаем информацию о векторной БД
            vector_path = self.vector_store.get_agent_vector_path(user_id, agent_id)
            
            # Подсчитываем документы
            docs_count = 0
            if vector_path.exists():
                try:
                    import chromadb
                    client = chromadb.PersistentClient(path=str(vector_path))
                    collection = client.get_collection(f"agent_{agent_id}_docs")
                    docs_count = collection.count()
                except:
                    pass
            
            return {
                "agent_id": agent_id,
                "documents_count": docs_count,
                "vector_db_path": str(vector_path),
                "ollama_status": self.ollama_service.test_connection()
            }
            
        except Exception as e:
            logger.error(f"Ошибка при получении статистики агента {agent_id}: {e}")
            return {"error": str(e)}
    
    async def send_response_to_telegram(
        self, 
        agent_id: int, 
        user_id: int, 
        query: str, 
        response: str, 
        db_session: AsyncSession
    ) -> Dict[str, Any]:
        """
        Отправляет ответ агента в Telegram чат
        
        Args:
            agent_id: ID агента
            user_id: ID пользователя
            query: Запрос пользователя
            response: Ответ агента
            db_session: Сессия БД
            
        Returns:
            Результат отправки
        """
        try:
            # Получаем Telegram конфигурацию агента
            from ..repositories.telegram_config import TelegramConfigRepository
            
            telegram_repo = TelegramConfigRepository(db_session)
            config = await telegram_repo.get_by_agent_id(agent_id)
            
            if not config or not config.is_active:
                return {
                    "success": False,
                    "error": "Telegram конфигурация не найдена или неактивна"
                }
            
            # Получаем информацию об агенте
            agent = await self._get_agent(agent_id, db_session)
            if not agent:
                return {
                    "success": False,
                    "error": "Агент не найден"
                }
            
            # Форматируем сообщение
            formatted_message = self.telegram_service.format_agent_response(
                agent.name, query, response
            )
            
            # Создаем объект сообщения
            message = TelegramMessage(
                chat_id=config.chat_id,
                text=formatted_message,
                parse_mode="HTML"
            )
            
            # Запускаем Celery задачу для отправки уведомления
            from src.tasks.telegram_tasks import send_telegram_notification
            
            task = send_telegram_notification.delay(
                agent_id=agent_id,
                user_id=user_id,
                query=query,
                response=response
            )
            
            logger.info(f"Telegram notification task started: {task.id}")
            
            return {
                "success": True,
                "task_id": task.id,
                "message": "Telegram уведомление поставлено в очередь"
            }
            
        except Exception as e:
            logger.error(f"Ошибка при отправке ответа в Telegram: {e}")
            return {
                "success": False,
                "error": str(e)
            }
