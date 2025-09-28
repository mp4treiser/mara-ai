from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
import os
import tempfile
import logging

from src.core.orm.database import get_async_session
from src.core.dependencies import get_current_user
from src.core.middlewares.subscription_middleware import require_active_subscription
from src.account.models.user import User
from src.agents.schemas.user_agent import (
    UserAgentCreate, UserAgentUpdate, UserAgentResponse, AgentWithUserAgentResponse
)
from src.agents.services.agent_service import AgentService
from src.agents.repositories.user_agent import UserAgentRepository

router = APIRouter(prefix="/user/agents", tags=["user-agents"])

# Инициализируем логгер
logger = logging.getLogger(__name__)

# Инициализируем сервисы
agent_service = AgentService()
user_agent_repo = None


def get_user_agent_repo(db: AsyncSession):
    """Получает репозиторий UserAgent"""
    global user_agent_repo
    if user_agent_repo is None:
        user_agent_repo = UserAgentRepository(db)
    return user_agent_repo


@router.get("/", response_model=List[AgentWithUserAgentResponse])
async def list_available_agents(
    current_user: User = Depends(require_active_subscription),
    db: AsyncSession = Depends(get_async_session)
):
    """Получает список всех доступных агентов с информацией о подключении пользователя"""
    try:
        repo = get_user_agent_repo(db)
        agents = await repo.get_all_agents_with_user_status(current_user.id)
        
        return [
            AgentWithUserAgentResponse(
                id=agent['id'],
                name=agent['name'],
                prompt=agent['prompt'],
                is_active=agent['is_active'],
                created_at=agent['created_at'],
                updated_at=agent['updated_at'],
                user_agent_id=agent['user_agent_id'],
                is_user_agent=agent['is_user_agent']
            )
            for agent in agents
        ]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при получении списка агентов: {str(e)}"
        )


@router.get("/my", response_model=List[UserAgentResponse])
async def list_my_agents(
    current_user: User = Depends(require_active_subscription),
    db: AsyncSession = Depends(get_async_session)
):
    """Получает список агентов пользователя"""
    try:
        repo = get_user_agent_repo(db)
        user_agents = await repo.get_user_agents(current_user.id)
        
        return [
            UserAgentResponse(
                id=ua.id,
                user_id=ua.user_id,
                agent_id=ua.agent_id,
                is_active=ua.is_active,
                created_at=ua.created_at,
                updated_at=ua.updated_at,
                agent_name=ua.agent.name,
                agent_prompt=ua.agent.prompt
            )
            for ua in user_agents
        ]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при получении списка агентов: {str(e)}"
        )


@router.post("/", response_model=UserAgentResponse)
async def connect_to_agent(
    user_agent_data: UserAgentCreate,
    current_user: User = Depends(require_active_subscription),
    db: AsyncSession = Depends(get_async_session)
):
    """Подключает пользователя к агенту"""
    try:
        repo = get_user_agent_repo(db)
        user_agent = await repo.create(user_agent_data, current_user.id)
        
        if not user_agent:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Не удалось подключиться к агенту. Возможно, агент не существует или уже подключен."
            )
        
        # Получаем информацию об агенте для ответа
        agent = await agent_service._get_agent(user_agent.agent_id, db)
        
        return UserAgentResponse(
            id=user_agent.id,
            user_id=user_agent.user_id,
            agent_id=user_agent.agent_id,
            is_active=user_agent.is_active,
            created_at=user_agent.created_at,
            updated_at=user_agent.updated_at,
            agent_name=agent.name,
            agent_prompt=agent.prompt
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при подключении к агенту: {str(e)}"
        )


@router.delete("/{user_agent_id}")
async def disconnect_from_agent(
    user_agent_id: int,
    current_user: User = Depends(require_active_subscription),
    db: AsyncSession = Depends(get_async_session)
):
    """Отключает пользователя от агента"""
    try:
        repo = get_user_agent_repo(db)
        
        # Проверяем, что связь принадлежит пользователю
        user_agent = await repo.get_by_id(user_agent_id)
        if not user_agent or user_agent.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Связь с агентом не найдена"
            )
        
        success = await repo.delete(user_agent_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Не удалось отключиться от агента"
            )
        
        return {"message": "Успешно отключились от агента"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при отключении от агента: {str(e)}"
        )


@router.post("/{user_agent_id}/documents")
async def upload_document_to_agent(
    user_agent_id: int,
    file: UploadFile = File(...),
    current_user: User = Depends(require_active_subscription),
    db: AsyncSession = Depends(get_async_session)
):
    """Загружает документ для агента пользователя"""
    try:
        repo = get_user_agent_repo(db)
        
        # Проверяем, что связь принадлежит пользователю
        user_agent = await repo.get_by_id(user_agent_id)
        if not user_agent or user_agent.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Связь с агентом не найдена"
            )
        
        # Проверяем, что связь активна
        if not user_agent.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Связь с агентом неактивна"
            )
        
        # Проверяем тип файла
        allowed_types = ['.txt', '.pdf', '.docx', '.doc', '.xlsx', '.xls']
        file_ext = os.path.splitext(file.filename)[1].lower()
        if file_ext not in allowed_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Неподдерживаемый тип файла. Разрешены: {', '.join(allowed_types)}"
            )
        
        # Сохраняем файл во временную директорию
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        try:
            # Сохраняем документ в БД
            from src.agents.repositories.document import DocumentRepository
            from src.agents.schemas.document import DocumentCreate
            
            document_repo = DocumentRepository(db)
            
            # Создаем запись о документе
            document_data = DocumentCreate(
                filename=file.filename,
                file_path=temp_file_path,
                file_type=file_ext[1:],  # Убираем точку
                file_size=len(content)
            )
            
            document = await document_repo.create(
                document_data=document_data,
                agent_id=user_agent.agent_id,
                user_id=current_user.id
            )
            
            # Обрабатываем документ синхронно
            from src.agents.services.agent_service import AgentService
            agent_service = AgentService()
            success = await agent_service.process_document(
                user_agent.agent_id, 
                current_user.id, 
                temp_file_path, 
                file.filename, 
                file_ext[1:], 
                db
            )
            if success:
                await document_repo.update_processed_status(document.id, True)
            
            return {
                "message": f"Документ {file.filename} загружен и обработан",
                "document_id": document.id
            }
            
        finally:
            # Удаляем временный файл
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
                
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при загрузке документа: {str(e)}"
        )


@router.post("/{user_agent_id}/analyze")
async def analyze_text_with_agent(
    user_agent_id: int,
    request: dict,
    current_user: User = Depends(require_active_subscription),
    db: AsyncSession = Depends(get_async_session)
):
    text = request.get('text', '')
    """Анализирует текст с помощью агента пользователя"""
    try:
        repo = get_user_agent_repo(db)
        
        # Проверяем, что связь принадлежит пользователю
        user_agent = await repo.get_by_id(user_agent_id)
        if not user_agent or user_agent.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Связь с агентом не найдена"
            )
        
        # Проверяем, что связь активна
        if not user_agent.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Связь с агентом неактивна"
            )
        
        # Анализируем текст
        result = await agent_service.analyze_text(
            user_agent.agent_id,
            current_user.id,
            text,
            db
        )
        
        if not result.get('success'):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result.get('error_message', 'Ошибка при анализе текста')
            )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при анализе текста: {str(e)}"
        )


@router.get("/{user_agent_id}/documents")
async def get_agent_documents(
    user_agent_id: int,
    current_user: User = Depends(require_active_subscription),
    db: AsyncSession = Depends(get_async_session)
):
    """Получает список документов агента пользователя"""
    try:
        repo = get_user_agent_repo(db)
        
        # Проверяем, что связь принадлежит пользователю
        user_agent = await repo.get_by_id(user_agent_id)
        if not user_agent or user_agent.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Связь с агентом не найдена"
            )
        
        # Получаем документы агента
        from src.agents.repositories.document import DocumentRepository
        document_repo = DocumentRepository(db)
        documents = await document_repo.get_by_agent_and_user(user_agent.agent_id, current_user.id)
        
        # Конвертируем в формат ответа
        from src.agents.schemas.document import DocumentResponse
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
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при получении документов: {str(e)}"
        )


@router.delete("/documents/{document_id}")
async def delete_document(
    document_id: int,
    current_user: User = Depends(require_active_subscription),
    db: AsyncSession = Depends(get_async_session)
):
    """Удаляет отдельный документ пользователя"""
    try:
        from src.agents.repositories.document import DocumentRepository
        document_repo = DocumentRepository(db)
        
        # Получаем документ
        document = await document_repo.get_by_id(document_id)
        
        if not document or document.user_id != current_user.id:
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


@router.delete("/{user_agent_id}/documents")
async def clear_agent_documents(
    user_agent_id: int,
    current_user: User = Depends(require_active_subscription),
    db: AsyncSession = Depends(get_async_session)
):
    """Очищает все документы агента пользователя"""
    try:
        repo = get_user_agent_repo(db)
        
        # Проверяем, что связь принадлежит пользователю
        user_agent = await repo.get_by_id(user_agent_id)
        if not user_agent or user_agent.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Связь с агентом не найдена"
            )
        
        # Проверяем, что связь активна
        if not user_agent.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Связь с агентом неактивна"
            )
        
        # Очищаем векторную базу данных агента
        success = agent_service.vector_store.delete_agent_collection(current_user.id, user_agent.agent_id)
        
        if success:
            return {"success": True, "message": "Все документы агента удалены"}
        else:
            return {"success": False, "message": "Ошибка при удалении документов"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при удалении документов: {str(e)}"
        )
