from datetime import datetime
from sqlalchemy import String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.core.orm.base import Base


class Agent(Base):
    __tablename__ = "agents"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)  # Название агента
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    prompt: Mapped[str] = mapped_column(Text, nullable=False)  # Промпт для агента
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)  # Активен ли агент
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="agents")
    documents: Mapped[list["Document"]] = relationship("Document", back_populates="agent", cascade="all, delete-orphan")
    logs: Mapped[list["AgentLog"]] = relationship("AgentLog", back_populates="agent", cascade="all, delete-orphan")
    user_agents: Mapped[list["UserAgent"]] = relationship("UserAgent", back_populates="agent")
    telegram_config: Mapped["TelegramConfig"] = relationship("TelegramConfig", back_populates="agent", uselist=False)
