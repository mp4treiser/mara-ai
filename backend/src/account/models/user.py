from datetime import datetime
from sqlalchemy import String, Boolean, DateTime, ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.core.orm.base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    company: Mapped[str] = mapped_column(String(255), nullable=True)
    first_name: Mapped[str] = mapped_column(String(255), nullable=True)
    last_name: Mapped[str] = mapped_column(String(255), nullable=True)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    balance: Mapped[float] = mapped_column(Numeric(10, 2), default=0.0)

    subscriptions: Mapped[list["Subscription"]] = relationship(back_populates="user")
    wallets: Mapped[list["Wallet"]] = relationship("Wallet", back_populates="user")
    agents: Mapped[list["Agent"]] = relationship("Agent", back_populates="user")
    user_agents: Mapped[list["UserAgent"]] = relationship("UserAgent", back_populates="user")
    documents: Mapped[list["Document"]] = relationship("Document", back_populates="user")
    telegram_configs: Mapped[list["TelegramConfig"]] = relationship("TelegramConfig", back_populates="user")
