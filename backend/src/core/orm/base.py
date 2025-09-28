import datetime

from typing import Annotated
from sqlalchemy import String, text
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase

# Аннотации для типов полей (больше не используются)
# str_255 = Annotated[str, String(255)]
# str_255_unique = Annotated[str, String(255)]
# bool_default_true = Annotated[bool, "default_true"]
# bool_default_false = Annotated[bool, "default_false"]
# date = Annotated[datetime.datetime, "timestamp"]

class Base(DeclarativeBase):
    __abstract__ = True

    created_at: Mapped[datetime.datetime] = mapped_column(server_default=text("TIMEZONE('utc', now())"))
    updated_at: Mapped[datetime.datetime] = mapped_column(server_default=text("TIMEZONE('utc', now())"))
