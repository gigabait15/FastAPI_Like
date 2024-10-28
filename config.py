import os
from dotenv import load_dotenv
from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict
)
from sqlalchemy import (
    create_engine,
    text
)

load_dotenv()


def create_database():
    """Функция создания БД"""
    temp_engine = create_engine(f"postgresql://{settings.DB_USER}:{settings.DB_PASSWORD}"
                                f"@{settings.DB_HOST}:{settings.DB_PORT}"
                                , isolation_level='AUTOCOMMIT')

    with temp_engine.connect() as conn:
        try:
            conn.execute(text(f"CREATE DATABASE {settings.DB_NAME};"))
            print(f'База данных {settings.DB_NAME} успешно создана')
        except Exception as e:
            print(f'Ошибка при создании БД: {e}')
        finally:
            conn.close()


class Settings(BaseSettings):
    """Класс модели для доступа к переменным окружения"""
    DB_HOST : str
    DB_PORT : int
    DB_NAME : str
    DB_USER : str
    DB_PASSWORD : str
    SECRET_KEY: str
    ALGORITHM: str

    model_config = SettingsConfigDict(
        env_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".." ,".env")
    )

    def get_db_url(self) -> str:
        """Функция возвращает ссылку на подключение к БД"""
        return (f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@"
                f"{self.DB_HOST}:{self.DB_PORT}/{settings.DB_NAME}")

    def get_auth_data(self) -> dict[str, str]:
        """Функция возвращает словарь с данными ключа приложения и алгоритма шифрования"""
        return {'secret_key': self.SECRET_KEY, 'algorithm': self.ALGORITHM}


# объявление переменной для ображение к экземпляру класса
settings = Settings()


