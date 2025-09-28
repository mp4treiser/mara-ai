from datetime import datetime
from pydantic import BaseModel, Field


class DocumentCreate(BaseModel):
    filename: str = Field(..., description="Имя файла")
    file_path: str = Field(..., description="Путь к файлу на диске")
    file_type: str = Field(..., description="Тип файла")
    file_size: int = Field(..., description="Размер файла в байтах")


class DocumentResponse(BaseModel):
    id: int
    agent_id: int
    user_id: int
    filename: str
    file_type: str
    file_size: int
    uploaded_at: datetime
    processed: bool

    class Config:
        from_attributes = True


class DocumentUpdate(BaseModel):
    processed: bool = Field(..., description="Статус обработки документа")
