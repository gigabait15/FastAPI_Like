from sqlalchemy import String
from sqlalchemy.orm import (
    Mapped,
    mapped_column
)
from database import (
    Base,
    str_uniq,
    int_pk,
    Gender,
    created_at
)


class User(Base):
    """Класс модели User для создания в таблице"""
    id: Mapped[int_pk]
    email: Mapped[str_uniq]
    password: Mapped[str]
    first_name: Mapped[str]
    last_name: Mapped[str]
    gender: Mapped[Gender]
    avatar: Mapped[str] = mapped_column(String)
    data_create_user: Mapped[created_at]
    latitude: Mapped[float]
    longitude: Mapped[float]


    extend_existing = True

    def __repr__(self):
        return f"{self.__class__.__name__}(id={self.id})"