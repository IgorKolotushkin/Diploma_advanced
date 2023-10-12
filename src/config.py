"""Модуль с настройками приложения."""
from functools import lru_cache
from typing import ClassVar

from pydantic_settings import BaseSettings, SettingsConfigDict

ODD_RESPONSES: dict = {
    200: {
        'description': 'Success',
        'content': {'application/json': {}},
    },
    404: {
        'description': 'Not Found',
        'content': {
            'application/json': {
                'example': {
                    'result': 'false',
                    'error_type': 'string',
                    'error_message': 'string',
                },
            },
        },
    },
    422: {
        'description': 'Validation error',
        'content': {
            'application/json': {
                'example': {
                    'result': 'false',
                    'error_type': 'string',
                    'error_message': 'string',
                },
            },
        },
    },
}


class Settings(BaseSettings):
    """Класс с базовыми настройками базы данных и загрузки их .env."""

    postgres_user: str
    postgres_password: str
    postgres_db: str
    host_db: str

    @property
    def db_url(self) -> str:
        """
        Метод формирования строки запроса к базе данных.

        Returns:
            str: строка с данными для базы данных
        """
        return 'postgresql+asyncpg://{passw}:{user}@{host}:5432/{db}'.format(
            passw=self.postgres_password,
            user=self.postgres_user,
            host=self.host_db,
            db=self.postgres_db,
        )

    model_config: ClassVar[SettingsConfigDict] = SettingsConfigDict(
        env_file='.env',
    )


@lru_cache()
def get_settings() -> Settings:
    """
    Функция для получения настроек базы данных.

    Returns:
        Settings: настройки базы данных из .env файла
    """
    return Settings()
