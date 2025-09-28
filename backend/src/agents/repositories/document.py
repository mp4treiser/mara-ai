from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.orm import selectinload
from datetime import datetime
from ..models.document import Document
from ..schemas.document import DocumentCreate


class DocumentRepository:
    """Репозиторий для работы с документами в БД"""
    
    def __init__(self, db_session: AsyncSession):
        self.db = db_session
    
    async def create(self, document_data: DocumentCreate, agent_id: int, user_id: int) -> Document:
        """Создает новый документ"""
        
        document = Document(
            agent_id=agent_id,
            user_id=user_id,
            filename=document_data.filename,
            file_path=document_data.file_path,
            file_type=document_data.file_type,
            file_size=document_data.file_size,
            uploaded_at=datetime.utcnow(),
            processed=False
        )
        
        self.db.add(document)
        await self.db.commit()
        await self.db.refresh(document)
        
        return document
    
    async def get_by_id(self, document_id: int) -> Optional[Document]:
        """Получает документ по ID"""
        result = await self.db.execute(
            select(Document).where(Document.id == document_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_agent_id(self, agent_id: int) -> List[Document]:
        """Получает все документы агента"""
        result = await self.db.execute(
            select(Document).where(Document.agent_id == agent_id)
        )
        return result.scalars().all()
    
    async def get_by_agent_and_user(self, agent_id: int, user_id: int) -> List[Document]:
        """Получает документы агента конкретного пользователя"""
        result = await self.db.execute(
            select(Document).where(
                Document.agent_id == agent_id,
                Document.user_id == user_id
            )
        )
        return result.scalars().all()
    
    async def get_by_user_id(self, user_id: int) -> List[Document]:
        """Получает все документы пользователя"""
        result = await self.db.execute(
            select(Document).where(Document.user_id == user_id)
        )
        return result.scalars().all()
    
    async def get_by_filename(self, agent_id: int, filename: str) -> Optional[Document]:
        """Получает документ по имени файла"""
        result = await self.db.execute(
            select(Document).where(
                Document.agent_id == agent_id,
                Document.filename == filename
            )
        )
        return result.scalar_one_or_none()
    
    async def get_by_filename_and_user(self, agent_id: int, filename: str, user_id: int) -> Optional[Document]:
        """Получает документ по имени файла для конкретного пользователя"""
        result = await self.db.execute(
            select(Document).where(
                Document.agent_id == agent_id,
                Document.filename == filename,
                Document.user_id == user_id
            )
        )
        return result.scalar_one_or_none()
    
    async def update_processed_status(self, document_id: int, processed: bool) -> Optional[Document]:
        """Обновляет статус обработки документа"""
        result = await self.db.execute(
            update(Document)
            .where(Document.id == document_id)
            .values(processed=processed)
            .returning(Document)
        )
        
        await self.db.commit()
        return result.scalar_one_or_none()
    
    async def delete(self, document_id: int) -> bool:
        """Удаляет документ"""
        result = await self.db.execute(
            delete(Document).where(Document.id == document_id)
        )
        await self.db.commit()
        return result.rowcount > 0
    
    async def delete_by_user(self, document_id: int, user_id: int) -> bool:
        """Удаляет документ с проверкой владельца"""
        result = await self.db.execute(
            delete(Document).where(
                Document.id == document_id,
                Document.user_id == user_id
            )
        )
        await self.db.commit()
        return result.rowcount > 0
    
    async def delete_by_agent_id(self, agent_id: int) -> bool:
        """Удаляет все документы агента"""
        result = await self.db.execute(
            delete(Document).where(Document.agent_id == agent_id)
        )
        await self.db.commit()
        return result.rowcount > 0
