from sqlalchemy import Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.core.orm.base import Base, str_255


class Plan(Base):
    __tablename__ = "plans"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str_255]
    days: Mapped[int] = mapped_column(Integer, nullable=False)
    price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    discount_percent: Mapped[float] = mapped_column(Numeric(5, 2), nullable=True)
    description: Mapped[str_255] = mapped_column(nullable=True)
    is_active: Mapped[bool] = mapped_column(default=True)

    subscriptions: Mapped[list["Subscription"]] = relationship(back_populates="plan")
