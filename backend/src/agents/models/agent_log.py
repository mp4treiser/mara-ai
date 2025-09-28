from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey, Text, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.core.orm.base import Base


class AgentLog(Base):
    __tablename__ = "agent_logs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    agent_id: Mapped[int] = mapped_column(ForeignKey("agents.id"), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)  # Пользователь, который использовал агента
    text_analyzed: Mapped[str] = mapped_column(Text, nullable=False)  # Анализируемый текст
    response: Mapped[str] = mapped_column(Text, nullable=False)  # Ответ агента
    processing_time: Mapped[float] = mapped_column(default=0.0)  # Время обработки в секундах
    text_length: Mapped[int] = mapped_column(Integer, default=0)  # Длина анализируемого текста
    documents_used: Mapped[int] = mapped_column(Integer, default=0)  # Количество документов использованных для контекста
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    agent: Mapped["Agent"] = relationship("Agent", back_populates="logs")
