from typing import (
    Optional,
    List
)
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
from database import Gender
from users.auth import (
    get_password_hash,
    authenticate_user,
    create_access_token
)
from users.dao import UsersDAO
from users.dependencies import get_current_user
from users.models import User
from users.schemas import SUserView
from utils.geo import get_geo, great_circle_distance
from utils.img_watermark import watermark_photo

router = APIRouter(prefix='/api', tags=['users'])


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
        avatar: UploadFile = File(default=None,description='Добавьте свой аватар или оставьте поле пустым')):
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
                    password: str = Form(...)):
    check = await authenticate_user(email=email, password=str(password))

    if check is None:
        return JSONResponse(content={"error": "Неверная почта или пароль"}, status_code=400)

    access_token = create_access_token({"sub": str(check.id)})
    response.set_cookie(key="users_access_token", value=access_token, httponly=True)
    return {'ok': True, 'access_token': access_token, 'refresh_token': None, 'message': 'Авторизация успешна!'}

@router.post("/logout/")
async def logout_user(response: Response):
    response.delete_cookie(key="users_access_token")
    return {'message': 'Пользователь успешно вышел из системы'}

@router.get("/me/", response_model=SUserView)
async def get_profile(current_user: User = Depends(get_current_user)):
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
):
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
