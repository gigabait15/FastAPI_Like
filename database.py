from datetime import datetime
from typing import Annotated
from enum import Enum
from sqlalchemy import func
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncAttrs,
    AsyncSession
)
from sqlalchemy.orm import (
    sessionmaker,
    mapped_column,
    DeclarativeBase,
    declared_attr
)
from config import settings

DATABASE_URL = settings.get_db_url()

engine = create_async_engine(DATABASE_URL, echo=True)

async_session_maker = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# настройка аннотаций
int_pk = Annotated[int, mapped_column(primary_key=True)]
str_uniq = Annotated[str, mapped_column(unique=True, nullable=False)]
str_null_true = Annotated[str, mapped_column(nullable=True)]
created_at = Annotated[datetime, mapped_column(server_default=func.now())]

class Gender(str, Enum):
    men = "men"
    women = "women"


class Base(AsyncAttrs, DeclarativeBase):
    """Абстрактный класс для создания таблиц"""
    __abstract__ = True

    @declared_attr.directive
    def __tablename__(cls) -> str:
        return f"{cls.__name__.lower()}s"
