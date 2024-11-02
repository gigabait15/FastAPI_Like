from datetime import datetime
from sqlalchemy import (
    String,
    ForeignKey,
    DateTime
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship
)
from database import (
    Base,
    str_uniq,
    int_pk,
    Gender,
    created_at,
)


class Grade(Base):
    """Класс для хранения истории оценок"""
    id: Mapped[int_pk]
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    email: Mapped[str] = mapped_column(String, nullable=False)
    date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    extend_existing = True


class User(Base):
    """Класс для хранения данных пользователя"""
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
    list_grade_history: Mapped[list[Grade]] = (
        relationship("Grade",
                     backref="user",
                     cascade="all, delete-orphan",)
    )


    extend_existing = True

    def __repr__(self):
        return f"{self.__class__.__name__}(id={self.id})"