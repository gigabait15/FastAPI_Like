from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from database import async_session_maker
from sqlalchemy import desc


class BaseDAO:
    model = None

    @classmethod
    async def find_all(cls, sort_by_date: bool = True, **filter_by):
        """
        Функция для получения всех объектов из таблицы с возможностью фильтрации и сортировки.
        :param filter_by: фильтры для поиска
        :param sort_by_date: если True, сортирует по дате создания от новых к старым
        :return: возвращает отфильтрованные и отсортированные объекты из таблицы
        """
        async with async_session_maker() as session:
            query = select(cls.model).filter_by(**filter_by)

            # Добавляем сортировку по дате создания
            if sort_by_date:
                query = query.order_by(desc(cls.model.data_create_user))

            result = await session.execute(query)
            return result.scalars().all()

    @classmethod
    async def find_by_id(cls, item_id: int):
        """
        Функция для получение одного объекта по id с таблицы
        :param item_id: обязательный параменр для поиска в таблице
        :return: объект из таблицы по указанному id
        """
        async with async_session_maker() as session:
            query = select(cls.model).filter_by(id=item_id)
            result = await session.execute(query)
            return result.scalar_one_or_none()

    @classmethod
    async def find_one_or_none(cls, **filter_by):
        """
        Функция для получение одного объекта с таблицы
        :param filter_by: необязательный параметр, в случае передачи будет поиск по указанному фильтру
        :return: объект из таблицы, если передан фильтр то выдаст объект по фильтру или None
        """
        async with async_session_maker() as session:
            query = select(cls.model).filter_by(**filter_by)
            result = await session.execute(query)
            return result.scalar_one_or_none()

    @classmethod
    async def add(cls, **values):
        """
        Функция для создания нового объекта в таблице
        :param values: обязательные параменты, которые определенны при создании таблицы
        :return: возвращает созданный объект
        """
        async with async_session_maker() as session:
            async with session.begin():
                new_instance = cls.model(**values)
                session.add(new_instance)
                try:
                    await session.commit()
                except SQLAlchemyError as e:
                    await session.rollback()
                    raise e
                return new_instance