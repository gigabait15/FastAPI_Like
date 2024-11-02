from datetime import datetime, timedelta
from typing import (
    Optional,
    List
)

from dns.e164 import query
from fastapi import (
    APIRouter,
    HTTPException,
    status,
    UploadFile,
    File,
    Form,
    Response,
    Depends,
    Query
)
from pydantic import EmailStr
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from database import (
    Gender,
    async_session_maker
)
from users.auth import (
    get_password_hash,
    authenticate_user,
    create_access_token
)
from users.dao import UsersDAO
from users.dependencies import get_current_user
from users.models import User, Grade
from users.schemas import SUserView
from utils.geo import (
    get_geo,
    great_circle_distance
)
from utils.img_watermark import watermark_photo
from utils.send_email import send_email_notification

router = APIRouter(prefix='/api', tags=['users'])

# Лимит оценок в день
DAILY_LIMIT:int = 5


@router.post('/clients/create/')
async def create_users(
        address: str = Form(default='Россия, Москва, ул.Тверская 1',
                            description='Введите свой адрес, в формате: Россия, Москва, ул.Тверская 1'),
        email: EmailStr = Form(...,description='Введите ваш email в формате user@example.com'),
        first_name: str = Form(...,description='Введите ваше имя'),
        last_name: str = Form(...,description='Введите вашу фамилию'),
        gender: Gender = Form(...,description='Выберите ваш пол'),
        password: str = Form(...,description='Введите пароль'),
        password_confirm: str = Form(...,description='Введите повторно пароль'),
        avatar: UploadFile = File(default=None,description='Добавьте свой аватар или оставьте поле пустым')) -> dict:
    """
    эндпоинт для регитсрации пользователя
    :param address: адрес пользователя для определения координат и сохранение их в экземпляре пользователя
    :param email: почта пользователя(должна быть уникальной)
    :param first_name: имя пользователя
    :param last_name: фамилия пользователя
    :param gender: пол пользователя
    :param password: пароль(в бд будет хешированая строка)
    :param password_confirm: проверка введенного пароля пользователем
    :param avatar: аватарка пользователя(по умолчанию ставится стандартная с водяным знаком)
    :return: возвращает данные зарегистрированого пользователя
    """
    user = await UsersDAO.find_one_or_none(email=email)
    if user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail=f'Пользователь c Email {email} уже существует')
    if password != password_confirm:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail='Пароли не совпадают')

    #шифрование(хеширование) пароля
    password_hash = get_password_hash(password)

    # добавление водяного знака
    output_avatar_path = f'{email}.png'
    avatar = await watermark_photo(avatar, output_avatar_path) \
        if avatar else 'users/avatars/default_avatar.png'

    # получения широты и долготы
    dict_geo = await get_geo(address)

    await UsersDAO.add(
        email=email,
        password=password_hash,
        first_name=first_name,
        last_name=last_name,
        gender=gender,
        avatar=avatar,
        latitude=dict_geo['latitude'] if 'latitude' in dict_geo else None,
        longitude=dict_geo['longitude'] if 'longitude' in dict_geo else None,
        list_grade_history=[]
    )

    created_user = await UsersDAO.find_one_or_none(email=email)
    user_view = SUserView(
        email=created_user.email,
        first_name=created_user.first_name,
        last_name=created_user.last_name,
        gender=created_user.gender,
        avatar=created_user.avatar,
        data_create_user = created_user.data_create_user,
        latitude=created_user.latitude,
        longitude=created_user.longitude,
    )
    return user_view

@router.post("/login/")
async def auth_user(response: Response,
                    email: EmailStr = Form(...),
                    password: str = Form(...)) -> dict:
    """
    эндпоинт для авторизации пользователя
    :param response: параметр для подключения
    :param email: обязательный параметр почта пользователя
    :param password: обязательный параметр пароль пользователя
    :return: токен в случае успешной авторизации
    """
    # проверка наличие данных пользователя в бд. так же проверка на соответствие пароля
    check = await authenticate_user(email=email, password=str(password))

    if check is None:
        return JSONResponse(content={"error": "Неверная почта или пароль"}, status_code=400)

    access_token = create_access_token({"sub": str(check.id)})
    response.set_cookie(key="users_access_token", value=access_token, httponly=True)
    return {'ok': True, 'access_token': access_token, 'refresh_token': None, 'message': 'Авторизация успешна!'}

@router.post("/logout/")
async def logout_user(response: Response) -> dict:
    """
    эндпоинт для выхода из учетной записи с удалением токена
    :param response: параметр для подключения
    :return: сообщение об выходе из системы
    """
    response.delete_cookie(key="users_access_token")
    return {'message': 'Пользователь успешно вышел из системы'}

@router.get("/me/", response_model=SUserView)
async def get_profile(current_user: User = Depends(get_current_user)) -> dict:
    """
    эндпоинт для просмотра профиля пользователя
    :param current_user: зависимость для получение данных пользователя
    :return: словарь с данными пользователя
    """
    return SUserView(
        email=current_user.email,
        first_name=current_user.first_name,
        last_name=current_user.last_name,
        gender=current_user.gender,
        avatar=current_user.avatar,
        data_create_user=current_user.data_create_user,
        latitude=current_user.latitude,
        longitude=current_user.longitude,
    )

@router.get("/list/", response_model=List[SUserView])
async def get_users(
    current_user: User = Depends(get_current_user),
    first_name: Optional[str] = Query(default=None),
    last_name: Optional[str] = Query(default=None),
    gender: Optional[str] = Query(default=None),
    sort_by_date: Optional[bool] = Query(default=True),
    distance: Optional[int] = Query(default=None)
) -> dict:
    """
    эндпоинт для получение списка пользователей по фильтрам если в них есть необходимость и сортировке по дате регистрации
    :param current_user: получение текущего пользователя
    :param first_name: имя для фильтра по имени
    :param last_name: фамилия для фильтра по фамилии
    :param gender: пол для фильтра по гендеру
    :param sort_by_date: сортировка по дате(по убыванию или по возрастанию)
    :param distance: фильтр для дистаниции
    :return: список пользователей в фиде словаря
    """
    # словарь для использование фильтров
    filters = {}
    if first_name:
        filters["first_name"] = first_name
    if last_name:
        filters["last_name"] = last_name
    if gender:
        filters["gender"] = gender

    # Получаем всех пользователей, кроме текущего
    users = [
        user for user in await UsersDAO.find_all(sort_by_date=sort_by_date, **filters)
        if user.id != current_user.id
    ]

    if not users:
        raise HTTPException(status_code=404, detail="Пользователи не найдены")

    # реализация для отображение пользователей по расстоянию
    if distance is not None:
        latlong_a = [current_user.latitude, current_user.longitude]
        users_within_distance = []

        for user in users:
            user_distance = await great_circle_distance([user.latitude, user.longitude], latlong_a)
            if user_distance < distance:
                user.distance = user_distance
                users_within_distance.append(user)

        if not users_within_distance:
            raise HTTPException(status_code=404,
                                detail="В пределах указанного расстояния не найдено ни одного пользователя")

        return users_within_distance

    return users

@router.get("/clients/{user_id}/match/", response_model=dict)
async def grade_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
) -> dict[str, str]:
    """
    Эндпоинт для создания симпатии. В случае взаимной симпатии
    отправляет обоим пользователям сообщение на электронную почту.
    Сохраняет симпатию для текущего пользователя и проверяет её наличие.

    :param user_id: ID пользователя, которому нужно поставить симпатию
    :param current_user: Зависимость для получения авторизованного пользователя
    :return: Сообщение об установке оценки
    """
    # Проверка, чтобы пользователь не оценивал сам себя
    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="Нельзя поставить симпатию самому себе")

    # Получаем пользователя по ID
    user = await UsersDAO.find_by_id(item_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    # Проверка лимита оценок в день
    now = datetime.utcnow()
    day_start = now - timedelta(days=1)
    daily_grades = [grade for grade in current_user.list_grade_history if grade.date >= day_start]
    if len(daily_grades) > DAILY_LIMIT:
        raise HTTPException(status_code=403, detail="Лимит оценок в день исчерпан")

    # Проверка на взаимную симпатию
    if user_id in [grade.user_id for grade in current_user.list_grade_history] and \
       current_user.id in [grade.user_id for grade in user.list_grade_history]:
        await send_email_notification(user1=current_user, user2=user)
        return {"message": "Взаимная симпатия!"}

    # Добавление симпатии
    new_grade = Grade(user_id=current_user.id, email=user.email, date=now)
    async with async_session_maker() as session:
        session.add(new_grade)
        await session.commit()

    return {"message": "Оценка добавлена"}