from fastapi import (
    APIRouter,
    HTTPException,
    status,
    UploadFile,
    File,
    Form,
    Response
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
from users.schemas import SUserView
from utils.img_watermark import watermark_photo

router = APIRouter(prefix='/api/clients', tags=['users'])


@router.post('/registration/')
async def create_users(
        email: EmailStr = Form(...),
        first_name: str = Form(...),
        last_name: str = Form(...),
        gender: Gender = Form(...),
        password: str = Form(...),
        password_confirm: str = Form(...),
        avatar: UploadFile = File(default=None)):
    user = await UsersDAO.find_one_or_none(email=email)
    if user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail=f'Пользователь c Email {email} уже существует')
    if password != password_confirm:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail='Пароли не совпадают')

    password_hash = get_password_hash(password)
    output_avatar_path = f'{email}.png'
    avatar = await watermark_photo(avatar, output_avatar_path) \
        if avatar else 'users/avatars/default_avatar.png'

    await UsersDAO.add(
        email=email,
        password=password_hash,
        first_name=first_name,
        last_name=last_name,
        gender=gender,
        avatar=avatar,
    )

    created_user = await UsersDAO.find_one_or_none(email=email)
    user_view = SUserView(
        email=created_user.email,
        first_name=created_user.first_name,
        last_name=created_user.last_name,
        gender=created_user.gender,
        avatar=created_user.avatar,
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

