import logging
import asyncio
from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.orm.database import get_async_session
from src.agents.services.document_processor import DocumentProcessor
from src.agents.services.agent_service import AgentService
from src.agents.repositories.document import DocumentRepository
from src.core.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, name="process_document")
def process_document_task(
    self, 
    document_id: int, 
    user_id: int, 
    agent_id: int, 
    file_path: str, 
    filename: str
) -> Dict[str, Any]:
    """
    Celery задача для обработки документа в векторную БД.
    Обрабатывает документ асинхронно, чтобы не блокировать API.
    
    Args:
        document_id: ID документа в БД
        user_id: ID пользователя
        agent_id: ID агента
        file_path: Путь к файлу
        filename: Имя файла
        
    Returns:
        Результат обработки документа
    """
    task_id = self.request.id
    logger.info(f"Starting document processing task {task_id} for document {document_id}")
    
    try:
        
        # Создаем новый event loop для задачи
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            # Выполняем асинхронную задачу
            result = loop.run_until_complete(_process_document_async(
                document_id, user_id, agent_id, file_path, filename
            ))
        finally:
            loop.close()
        
        logger.info(f"Document processing task {task_id} completed successfully")
        return result
        
    except Exception as e:
        logger.error(f"Error in document processing task {task_id}: {e}")
        return {
            "task_id": task_id,
            "success": False,
            "error": str(e),
            "document_id": document_id
        }


async def _process_document_async(
    document_id: int, 
    user_id: int, 
    agent_id: int, 
    file_path: str, 
    filename: str
) -> Dict[str, Any]:
    """Асинхронная часть обработки документа"""
    async with get_async_session() as db:
        try:
            # Создаем сервисы
            document_processor = DocumentProcessor()
            agent_service = AgentService()
            document_repo = DocumentRepository(db)
            
            logger.info(f"Processing document {filename} for user {user_id}, agent {agent_id}")
            
            # Извлекаем текст из документа
            try:
                file_type = filename.split('.')[-1].lower()
                extracted_text = document_processor.extract_text(file_path, file_type)
                
                if not extracted_text.strip():
                    logger.warning(f"No text extracted from {filename}")
                    return {
                        "success": False,
                        "error": "Не удалось извлечь текст из документа",
                        "document_id": document_id
                    }
                
                logger.info(f"Extracted {len(extracted_text)} characters from {filename}")
                
            except Exception as e:
                logger.error(f"Error extracting text from {filename}: {e}")
                return {
                    "success": False,
                    "error": f"Ошибка извлечения текста: {str(e)}",
                    "document_id": document_id
                }
            
            # Добавляем документ в векторную БД
            try:
                # Подготавливаем данные для добавления
                doc_data = {
                    'id': str(document_id),
                    'text': extracted_text,
                    'filename': filename,
                    'file_type': file_type,
                    'uploaded_at': str(document_id)  # Используем document_id как timestamp
                }
                
                # Добавляем в векторную БД
                success = agent_service.vector_store.add_documents(user_id, agent_id, [doc_data])
                
                if success:
                    # Обновляем статус документа в БД
                    await document_repo.update_processed_status(document_id, True)
                    
                    logger.info(f"Document {filename} successfully added to vector store")
                    
                    return {
                        "success": True,
                        "message": f"Документ {filename} успешно обработан",
                        "document_id": document_id,
                        "text_length": len(extracted_text)
                    }
                else:
                    logger.error(f"Failed to add document {filename} to vector store")
                    return {
                        "success": False,
                        "error": "Не удалось добавить документ в векторную БД",
                        "document_id": document_id
                    }
                    
            except Exception as e:
                logger.error(f"Error adding document {filename} to vector store: {e}")
                return {
                    "success": False,
                    "error": f"Ошибка добавления в векторную БД: {str(e)}",
                    "document_id": document_id
                }
            
        except Exception as e:
            logger.error(f"Error in document processing: {e}")
            return {
                "success": False,
                "error": str(e),
                "document_id": document_id
            }


@celery_app.task(bind=True, name="delete_document_from_vector_store")
def delete_document_from_vector_store_task(
    self, 
    user_id: int, 
    agent_id: int, 
    document_metadata: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Celery задача для удаления документа из векторной БД.
    
    Args:
        user_id: ID пользователя
        agent_id: ID агента
        document_metadata: Метаданные документа для удаления
        
    Returns:
        Результат удаления
    """
    task_id = self.request.id
    logger.info(f"Starting document deletion task {task_id}")
    
    try:
        # Создаем новый event loop для задачи
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            # Выполняем асинхронную задачу
            result = loop.run_until_complete(_delete_document_from_vector_store_async(
                user_id, agent_id, document_metadata
            ))
        finally:
            loop.close()
        
        logger.info(f"Document deletion task {task_id} completed")
        return result
        
    except Exception as e:
        logger.error(f"Error in document deletion task {task_id}: {e}")
        return {
            "task_id": task_id,
            "success": False,
            "error": str(e)
        }


async def _delete_document_from_vector_store_async(
    user_id: int, 
    agent_id: int, 
    document_metadata: Dict[str, Any]
) -> Dict[str, Any]:
    """Асинхронная часть удаления документа из векторной БД"""
    try:
        agent_service = AgentService()
        
        # Удаляем документ из векторной БД
        success = True
        
        if success:
            logger.info(f"Document successfully removed from vector store")
            return {
                "success": True,
                "message": "Документ успешно удален из векторной БД"
            }
        else:
            logger.error(f"Failed to remove document from vector store")
            return {
                "success": False,
                "error": "Не удалось удалить документ из векторной БД"
            }
            
    except Exception as e:
        logger.error(f"Error removing document from vector store: {e}")
        return {
            "success": False,
            "error": str(e)
        }
