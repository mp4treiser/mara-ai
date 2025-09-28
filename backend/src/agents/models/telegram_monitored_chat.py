from datetime import datetime
from sqlalchemy import ForeignKey, String, Boolean, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.core.orm.base import Base


class TelegramMonitoredChat(Base):
    """Модель для чатов, которые мониторятся на предмет алертов"""
    
    __tablename__ = "telegram_monitored_chats"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    telegram_config_id: Mapped[int] = mapped_column(ForeignKey("telegram_configs.id"), nullable=False)
    chat_id: Mapped[str] = mapped_column(String(255), nullable=False)  # ID чата для мониторинга
    chat_title: Mapped[str] = mapped_column(String(255), nullable=True)  # Название чата
    chat_type: Mapped[str] = mapped_column(String(50), nullable=False)  # Тип чата (group, supergroup, channel)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    keywords: Mapped[str] = mapped_column(Text, nullable=True)  # Ключевые слова для фильтрации (JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Связи
    telegram_config: Mapped["TelegramConfig"] = relationship("TelegramConfig", back_populates="monitored_chats")
