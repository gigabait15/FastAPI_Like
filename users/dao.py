from DAO.base import BaseDAO
from database import async_session_maker
from users.models import User
from sqlalchemy import select


class UsersDAO(BaseDAO):
    model = User

    @classmethod
    async def find_one_or_none(cls, email: str):
        """
        Функция для получение объектa из таблицы по указанному email либо None
        :param email: email пользователя для поиска
        :return: возвращает объект из таблицы
        """
        async with async_session_maker() as session:
            query = select(cls.model).filter_by(email=email)
            result = await session.execute(query)
            return result.scalar_one_or_none()

