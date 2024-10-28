from typing import Optional
from pydantic import (
    BaseModel,
    EmailStr,
    Field,
    ConfigDict
)
from sqlalchemy import Enum
from database import Gender


class SUserRegister(BaseModel):
    """класс с полями которые должны передаваться при регистрации пользователя"""
    model_config = ConfigDict(from_attributes=True)
    email: EmailStr = Field(..., description="Электронная почта")
    first_name: str = Field(..., min_length=2, max_digits=50, description='Имя, от 2 до 50 знаков')
    last_name: str = Field(..., min_length=2, max_digits=50, description='Фамилия, от 2 до 50 знаков')
    gender: Enum[Gender] = Field(..., description='Гендер')
    password: str = Field(..., min_length=4, max_length=50, description="Пароль, от 4 до 50 знаков")
    password_confirm: str = Field(..., min_length=4, max_length=50, description="Пароль, от 4 до 50 знаков")
    avatar: Optional[str] = Field(default='users/avatars/default_avatar.png',
                                  description="URL аватара пользователя (по умолчанию)")


class SUserAuth(BaseModel):
    """класс с полями которые должны передаваться при авторизации пользователя"""
    email: EmailStr = Field(..., description="Электронная почта")
    password: str = Field(..., min_length=4, max_length=50, description="Пароль, от 4 до 50 знаков")


