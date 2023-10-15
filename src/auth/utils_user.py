"""Модуль с дополнительными функциями."""

from fastapi import Request
from passlib.context import CryptContext

pwd_context: CryptContext = CryptContext(schemes=['bcrypt'], deprecated='auto')


def hash_password(password) -> str:
    """
    Функция получения хэшированного пароля для пользователя.

    Args:
        password: пароль введенный пользователем

    Returns:
        str: хэшированный пароль
    """
    return pwd_context.hash(password)


def validate_password(password: str, hashed_password: str) -> bool:
    """
    Функция сравнения пароля введенного пользователем и пароля в базе данных.

    Args:
        password: пароль введенный пользователем
        hashed_password: пароль в базе данных

    Returns:
        bool: True, если пароли совпадают, False, если нет
    """
    return pwd_context.verify(password, hashed_password)


async def get_apikey_from_headers(request: Request) -> str:
    """
    Функция получения api-key текущего пользователя из headers.

    Args:
        request: Request

    Returns:
        str: api-key текущего пользователя
    """
    api_key: str = request.headers.get('api-key', None)
    if api_key != 'null' and api_key is not None:
        return api_key
