from sqlalchemy.orm import joinedload
from DAO.base import BaseDAO
from database import async_session_maker
from users.models import User
from sqlalchemy import select, desc


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

    @classmethod
    async def find_all(cls, sort_by_date: bool = True, **filter_by):
        """
        Переопределение функции, добавлена загрузка list_grade_history
        Функция для получения всех объектов из таблицы с возможностью фильтрации и сортировки.
        :param filter_by: фильтры для поиска
        :param sort_by_date: если True, сортирует по дате создания от новых к старым
        :return: возвращает отфильтрованные и отсортированные объекты из таблицы
        """
        async with async_session_maker() as session:
            query = select(cls.model).options(joinedload(User.list_grade_history)).filter_by(**filter_by)

            # Добавляем сортировку по дате создания
            if sort_by_date:
                query = query.order_by(desc(cls.model.data_create_user))

            result = await session.execute(query)
            return result.unique().scalars().all()

