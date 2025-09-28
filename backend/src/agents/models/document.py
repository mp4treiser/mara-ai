from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.core.orm.base import Base


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    agent_id: Mapped[int] = mapped_column(ForeignKey("agents.id"), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)  # Владелец документа
    filename: Mapped[str] = mapped_column(String(255), nullable=False)  # Оригинальное имя файла
    file_path: Mapped[str] = mapped_column(Text, nullable=False)  # Путь к файлу на диске
    file_type: Mapped[str] = mapped_column(String(255), nullable=False)  # Тип файла (pdf, xlsx, docx)
    file_size: Mapped[int]  # Размер файла в байтах
    uploaded_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    processed: Mapped[bool] = mapped_column(default=False)  # Обработан ли файл в векторную БД

    # Relationships
    agent: Mapped["Agent"] = relationship("Agent", back_populates="documents")
    user: Mapped["User"] = relationship("User", back_populates="documents")
