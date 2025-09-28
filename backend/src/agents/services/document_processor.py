import os
import shutil
import logging
from pathlib import Path
from typing import List, Dict, Any
from ..utils.file_handlers import FileProcessor

logger = logging.getLogger(__name__)


class DocumentProcessor:
    """Сервис для обработки и загрузки документов"""
    
    def __init__(self, base_path: str = "docs"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(exist_ok=True)
        self.file_processor = FileProcessor()
    
    def get_agent_docs_path(self, user_id: int, agent_id: int) -> Path:
        """Получает путь к папке документов агента"""
        return self.base_path / str(user_id) / str(agent_id) / "documents"
    
    def save_uploaded_file(self, user_id: int, agent_id: int, file, filename: str) -> Dict[str, Any]:
        """Сохраняет загруженный файл"""
        logger.info(f"Начало загрузки файла {filename} для пользователя {user_id}, агента {agent_id}")
        try:
            # Создаем папку для документов агента
            docs_path = self.get_agent_docs_path(user_id, agent_id)
            docs_path.mkdir(parents=True, exist_ok=True)
            logger.debug(f"Создана папка для документов: {docs_path}")
            
            # Генерируем уникальное имя файла
            file_extension = Path(filename).suffix
            unique_filename = f"{int(os.urandom(4).hex(), 16)}_{filename}"
            file_path = docs_path / unique_filename
            
            # Сохраняем файл
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            # Получаем размер файла
            file_size = os.path.getsize(file_path)
            logger.info(f"Файл {filename} сохранен, размер: {file_size} байт")
            
            # Определяем тип файла
            file_type = file_extension.lower().lstrip('.')
            logger.debug(f"Определен тип файла: {file_type}")
            
            # Получаем список поддерживаемых типов
            supported_types = self.file_processor.get_supported_types()
            logger.info(f"Поддерживаемые типы файлов: {supported_types}")
            logger.info(f"Проверяем тип файла: {file_type}")
            
            # Проверяем поддержку типа файла
            if file_type not in supported_types:
                # Удаляем неподдерживаемый файл
                os.remove(file_path)
                logger.warning(f"Неподдерживаемый тип файла {file_type} для файла {filename}")
                return {
                    "success": False,
                    "error": f"Неподдерживаемый тип файла: {file_type}. Разрешены: {', '.join(supported_types)} "
                }
            
            logger.info(f"Файл {filename} успешно загружен для агента {agent_id}")
            return {
                "success": True,
                "filename": unique_filename,
                "original_filename": filename,
                "file_path": str(file_path),
                "file_type": file_type,
                "file_size": file_size
            }
            
        except Exception as e:
            logger.error(f"Ошибка при сохранении файла {filename}: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def extract_text(self, file_path: str, file_type: str) -> str:
        """Извлекает текст из документа"""
        try:
            return self.file_processor.extract_text(file_path, file_type)
        except Exception as e:
            logger.error(f"Ошибка при извлечении текста из {file_path}: {e}")
            raise
    
    def delete_document(self, user_id: int, agent_id: int, filename: str) -> bool:
        """Удаляет документ"""
        try:
            docs_path = self.get_agent_docs_path(user_id, agent_id)
            file_path = docs_path / filename
            
            if file_path.exists():
                os.remove(file_path)
                logger.info(f"Документ {filename} удален")
                return True
            else:
                logger.warning(f"Файл {filename} не найден для удаления")
                return False
                
        except Exception as e:
            logger.error(f"Ошибка при удалении документа {filename}: {e}")
            return False
    
    def get_documents_list(self, user_id: int, agent_id: int) -> List[Dict[str, Any]]:
        """Получает список документов агента"""
        try:
            docs_path = self.get_agent_docs_path(user_id, agent_id)
            
            if not docs_path.exists():
                return []
            
            documents = []
            for file_path in docs_path.iterdir():
                if file_path.is_file():
                    documents.append({
                        "filename": file_path.name,
                        "file_size": os.path.getsize(file_path),
                        "file_type": file_path.suffix.lower().lstrip('.'),
                        "modified_at": os.path.getmtime(file_path)
                    })
            
            return documents
            
        except Exception as e:
            logger.error(f"Ошибка при получении списка документов: {e}")
            return []
    
    def cleanup_agent_documents(self, user_id: int, agent_id: int) -> bool:
        """Очищает все документы агента"""
        try:
            docs_path = self.get_agent_docs_path(user_id, agent_id)
            
            if docs_path.exists():
                shutil.rmtree(docs_path)
                logger.info(f"Документы агента {agent_id} очищены")
                return True
            
            return True
            
        except Exception as e:
            logger.error(f"Ошибка при очистке документов агента {agent_id}: {e}")
            return False
    
    def get_supported_file_types(self) -> List[str]:
        """Возвращает список поддерживаемых типов файлов"""
        return self.file_processor.get_supported_types()
    
    def validate_file_size(self, file_size: int, max_size_mb: int = 50) -> bool:
        """Проверяет размер файла"""
        max_size_bytes = max_size_mb * 1024 * 1024
        return file_size <= max_size_bytes
