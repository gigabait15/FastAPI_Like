from fastapi import Request, HTTPException, status, Depends
from jose import jwt, JWTError
from datetime import datetime, timezone
from config import settings
from users.dao import UsersDAO


def get_token(request: Request):
    """
     Извлекает токен из cookies запроса. Если токен отсутствует, выбрасывается исключение .
    """
    token = request.cookies.get('users_access_token')
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Отсутствует токен')
    return token


async def get_current_user(token: str = Depends(get_token)):
    """
    Декодирует токен с использованием секретного ключа и алгоритма из конфигурации.
    Проверяет срок действия токена. Если токен истек, выбрасывается исключение .
    Извлекает ID пользователя из токена. Если ID отсутствует, выбрасывается исключение .
    Ищет пользователя в базе данных по ID. Если пользователь не найден, выбрасывается исключение .
    """
    try:
        auth_data = settings.get_auth_data()
        payload = jwt.decode(token, auth_data['secret_key'], algorithms=[auth_data['algorithm']])
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Токен не валидный!')

    expire = payload.get('exp')
    expire_time = datetime.fromtimestamp(int(expire), tz=timezone.utc)
    if (not expire) or (expire_time < datetime.now(timezone.utc)):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Токен истек')

    user_id = payload.get('sub')
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Не найден ID пользователя')

    user = await UsersDAO.find_one_or_none_by_id(int(user_id))
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f'Не найден пользователь с ID {user_id}')

    return user
