from datetime import datetime
from sqlalchemy import String, Boolean, DateTime, ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.core.orm.base import Base, str_255, str_255_unique, bool_default_false, bool_default_true


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    email: Mapped[str_255_unique]
    password: Mapped[str_255]
    company: Mapped[str_255]
    first_name: Mapped[str_255]
    last_name: Mapped[str_255]
    is_superuser: Mapped[bool_default_false]
    is_active: Mapped[bool_default_true]
    balance: Mapped[float] = mapped_column(Numeric(10, 2), default=0.0)

    subscriptions: Mapped[list["Subscription"]] = relationship(back_populates="user")
    wallets: Mapped[list["Wallet"]] = relationship("Wallet", back_populates="user")
