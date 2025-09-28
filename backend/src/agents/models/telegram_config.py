from datetime import datetime
from sqlalchemy import String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.core.orm.base import Base


class TelegramConfig(Base):
    __tablename__ = "telegram_configs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    agent_id: Mapped[int] = mapped_column(ForeignKey("agents.id"), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    bot_token: Mapped[str] = mapped_column(Text, nullable=False)  # Токен бота
    chat_id: Mapped[str] = mapped_column(String(255), nullable=False)  # ID чата для отправки
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)  # Активна ли интеграция
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    agent: Mapped["Agent"] = relationship("Agent", back_populates="telegram_config")
    user: Mapped["User"] = relationship("User", back_populates="telegram_configs")
    monitored_chats: Mapped[list["TelegramMonitoredChat"]] = relationship("TelegramMonitoredChat", back_populates="telegram_config", cascade="all, delete-orphan")
