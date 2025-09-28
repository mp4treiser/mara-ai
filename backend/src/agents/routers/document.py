import logging
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from src.core.orm.database import get_async_session
from src.core.dependencies import get_current_user
from src.core.middlewares.subscription_middleware import require_active_subscription
from src.account.models.user import User
from src.account.services import SubscriptionService
from src.agents.schemas.document import DocumentResponse, DocumentCreate
from src.agents.services.document_processor import DocumentProcessor
from src.agents.services.agent_service import AgentService
from src.agents.repositories.document import DocumentRepository

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/agents", tags=["documents"])

# Инициализируем сервисы
document_processor = DocumentProcessor()
agent_service = AgentService()


@router.post("/{agent_id}/documents/upload")
async def upload_document(
    agent_id: int,
    file: UploadFile = File(...),
    current_user: User = Depends(require_active_subscription),
    db: AsyncSession = Depends(get_async_session)
):
    """
    Загружает документ для агента.
    Требует активную подписку.
    """
    
    # Проверяем активную подписку
    subscription_service = SubscriptionService(session=db)
    active_subscriptions = await subscription_service.get_active_by_user_id(current_user.id)
    
    if not active_subscriptions:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Требуется активная подписка для загрузки документов"
        )
    
    try:
        # Проверяем размер файла (максимум 50MB)
        if not document_processor.validate_file_size(file.size):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Размер файла превышает 50MB"
            )
        
        # Сохраняем файл на диск
        result = document_processor.save_uploaded_file(
            user_id=current_user.id,
            agent_id=agent_id,
            file=file,
            filename=file.filename
        )
        
        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["error"]
            )
        
        # Сохраняем документ в БД
        document_repo = DocumentRepository(db)
        document_data = DocumentCreate(
            filename=result["filename"],
            file_path=result["file_path"],
            file_type=result["file_type"],
            file_size=result["file_size"]
        )
        
        document = await document_repo.create(document_data, agent_id, current_user.id)
        
        # Обрабатываем документ для векторной БД
        try:
            # Извлекаем текст из документа
            text = document_processor.extract_text(result["file_path"], result["file_type"])
            
            if text:
                # Добавляем в векторную БД
                doc_data = {
                    'id': str(document.id),
                    'text': text,
                    'filename': result["filename"],
                    'file_type': result["file_type"],
                    'uploaded_at': document.uploaded_at.isoformat()
                }
                
                success = agent_service.vector_store.add_documents(current_user.id, agent_id, [doc_data])
                
                if success:
                    # Обновляем статус обработки
                    await document_repo.update_processed_status(document.id, True)
                    logger.info(f"Документ {result['filename']} успешно обработан для агента {agent_id}")
                else:
                    logger.warning(f"Не удалось добавить документ {result['filename']} в векторную БД")
            else:
                logger.warning(f"Не удалось извлечь текст из документа {result['filename']}")
                
        except Exception as e:
            logger.error(f"Ошибка при обработке документа {result['filename']}: {e}")
            # Документ остается в БД, но с флагом processed=False
        
        return {
            "success": True,
            "message": "Документ успешно загружен",
            "document_id": document.id,
            "filename": result["filename"],
            "original_filename": result["original_filename"],
            "file_size": result["file_size"],
            "file_type": result["file_type"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при загрузке документа: {str(e)}"
        )


@router.get("/{agent_id}/documents", response_model=List[DocumentResponse])
async def list_documents(
    agent_id: int,
    current_user: User = Depends(require_active_subscription),
    db: AsyncSession = Depends(get_async_session)
):
    """
    Получает список документов агента.
    Требует активную подписку.
    """
    
    # Проверяем активную подписку
    subscription_service = SubscriptionService(session=db)
    active_subscriptions = await subscription_service.get_active_by_user_id(current_user.id)
    
    if not active_subscriptions:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Требуется активная подписка для просмотра документов"
        )
    
    try:
        # Получаем документы из БД (только текущего пользователя)
        document_repo = DocumentRepository(db)
        documents = await document_repo.get_by_agent_and_user(agent_id, current_user.id)
        
        # Конвертируем в формат DocumentResponse
        response_documents = []
        for doc in documents:
            response_documents.append(DocumentResponse(
                id=doc.id,
                agent_id=doc.agent_id,
                user_id=doc.user_id,
                filename=doc.filename,
                file_type=doc.file_type,
                file_size=doc.file_size,
                uploaded_at=doc.uploaded_at,
                processed=doc.processed
            ))
        
        return response_documents
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при получении списка документов: {str(e)}"
        )


@router.delete("/{agent_id}/documents/{document_id}")
async def delete_document(
    agent_id: int,
    document_id: int,
    current_user: User = Depends(require_active_subscription),
    db: AsyncSession = Depends(get_async_session)
):
    """
    Удаляет документ агента.
    Требует активную подписку.
    """
    
    # Проверяем активную подписку
    subscription_service = SubscriptionService(session=db)
    active_subscriptions = await subscription_service.get_active_by_user_id(current_user.id)
    
    if not active_subscriptions:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Требуется активная подписка для удаления документов"
        )
    
    try:
        # Получаем документ
        document_repo = DocumentRepository(db)
        document = await document_repo.get_by_id(document_id)
        
        if not document or document.agent_id != agent_id or document.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Документ не найден"
            )
        
        # Удаляем из векторной БД (если был обработан)
        if document.processed:
            try:
                # Здесь можно добавить логику удаления из векторной БД
                pass
            except Exception as e:
                logger.warning(f"Не удалось удалить документ {document.filename} из векторной БД: {e}")
        
        # Удаляем файл с диска
        try:
            import os
            if os.path.exists(document.file_path):
                os.remove(document.file_path)
        except Exception as e:
            logger.warning(f"Не удалось удалить файл {document.file_path}: {e}")
        
        # Удаляем запись из БД (с проверкой владельца)
        success = await document_repo.delete_by_user(document_id, current_user.id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Не удалось удалить документ из БД"
            )
        
        return {"success": True, "message": "Документ успешно удален"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при удалении документа: {str(e)}"
        )


@router.get("/supported-file-types")
async def get_supported_file_types():
    """Получает список поддерживаемых типов файлов"""
    try:
        supported_types = document_processor.get_supported_file_types()
        return {"supported_types": supported_types}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при получении поддерживаемых типов файлов: {str(e)}"
        )
