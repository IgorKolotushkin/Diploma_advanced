"""Основной модуль с эндпоинтами с информацией пользователя."""
from typing import Annotated, Type

from fastapi import APIRouter, Depends, Security, status
from fastapi.exceptions import HTTPException
from fastapi.security import APIKeyHeader
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import DBAPIError
from src.auth.schemas import (
    UserLoginSchema,
    ApiKeySchema,
    UserRegisterSchema,
    UserSchema,
    UserMeSchema,
    ResultSchema,
)
from src.auth.crud import (
    get_user_by_email,
    get_user_apikey,
    get_user_by_apikey,
    create_user,
    get_all_info_user,
    delete_follower_by_id,
    add_follower_by_id,
)
from src.auth.utils_user import validate_password, get_apikey_from_headers
from src.auth.models import User
from src.config import ODD_RESPONSES
from src.database import get_session

router: APIRouter = APIRouter(prefix='', tags=['Auth'])
api_key_header: APIKeyHeader = APIKeyHeader(name='api-key')


@router.post('/login', response_model=ApiKeySchema, responses=ODD_RESPONSES)
async def auth(
    user: UserLoginSchema,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> str:
    """
    Endpoint для авторизации пользователя.

    Args:
        user: UserLoginSchema(login, password)
        session: асинхронная сессия для подключения к базе данных

    Returns:
        str: api-key зарегистрированного пользователя

    Raises:
        HTTPException: если неправильный пароль или email
    """
    user_db: User | None = await get_user_by_email(
        email=user.email,
        session=session,
    )
    if not user_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Incorrect email',
        )
    valid_pass: bool = validate_password(
        password=user.password,
        hashed_password=user_db.password,
    )
    if not valid_pass:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Invalid password',
        )

    return await get_user_apikey(user_id=user_db.id, session=session)


@router.post(
    '/register',
    response_model=ApiKeySchema,
    responses=ODD_RESPONSES,
)
async def create_new_user(
    user: UserRegisterSchema,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> str:
    """
    Endpoint для регистрации пользователя.

    Args:
        user: UserRegisterSchema(login, password, password2)
        session: асинхронная сессия для подключения к базе данных

    Returns:
        str: api-key зарегистрированного пользователя

    Raises:
        HTTPException: Если пользователь уже существует
    """
    exist_user: User | None = await get_user_by_email(
        email=user.email,
        session=session,
    )
    if exist_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='User with this email already exists',
        )

    return await create_user(user=user, session=session)


async def get_current_user(
    api_key: Annotated[str, Depends(get_apikey_from_headers)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> User:
    """
    Функция для получения текущего пользователя.

    Args:
        api_key: api-key текущего пользователя, полученный из headers
        session: асинхронная сессия для подключения к базе данных

    Returns:
        User: текущий пользователь

    Raises:
        HTTPException: если api-key не UUID
    """
    try:
        return await get_user_by_apikey(apikey=api_key, session=session)
    except (ValueError, DBAPIError):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Invalid ApiKey',
        )


@router.get(
    '/users/me',
    response_model=UserMeSchema,
    responses=ODD_RESPONSES,
    dependencies=[Security(api_key_header)],
)
async def get_user_me(
    user: Annotated[UserSchema, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> UserMeSchema:
    """
    Endpoint для получения информации из профиля для текущего пользователя.

    Args:
        user: UserSchema - авторизированный пользователь
        session: асинхронная сессия для подключения к базе данных

    Returns:
        UserMeSchema: информация о профиле пользователя

    Raises:
        HTTPException: если пользователь не авторизован
    """
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    user_db = await get_all_info_user(user_id=user.id, session=session)
    return UserMeSchema(user=user_db)


@router.get(
    '/users/{idx}',
    response_model=UserMeSchema,
    responses=ODD_RESPONSES,
    dependencies=[Security(api_key_header)],
)
async def get_user_by_id(
    idx: int,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> UserMeSchema:
    """
    Endpoint для получения информации из профиля для пользователя по id.

    Args:
        idx: id пользователя по которому запрашивается информация
        session: асинхронная сессия для подключения к базе данных

    Returns:
        UserMeSchema: информация о профиле пользователя

    Raises:
        HTTPException: если пользователя нет в базе данных
    """
    user_db = await get_all_info_user(user_id=idx, session=session)
    if not user_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    return UserMeSchema(user=user_db)


@router.post(
    '/users/{idx}/follow',
    response_model=ResultSchema,
    responses=ODD_RESPONSES,
    dependencies=[Security(api_key_header)],
)
async def add_new_follower(
    idx: int,
    user: Annotated[UserSchema, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> Type[ResultSchema]:
    """
    Endpoint для подписки на пользователя по его id.

    Args:
        idx: id пользователя на которого нужно подписаться
        user: текущий авторизованный пользователь
        session: асинхронная сессия для подключения к базе данных

    Returns:
        ResultSchema: простой ответ, что подписка прошла успешно

    Raises:
        HTTPException: если пользователя не авторизован
    """
    if not user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    await add_follower_by_id(idx=idx, user_id=user.id, session=session)
    return ResultSchema


@router.delete(
    '/users/{idx}/follow',
    response_model=ResultSchema,
    responses=ODD_RESPONSES,
    dependencies=[Security(api_key_header)],
)
async def delete_follower(
    idx: int,
    user: Annotated[UserSchema, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> Type[ResultSchema]:
    """
    Endpoint для удаления подписки на пользователя по его id.

    Args:
        idx: id пользователя по которому запрашивается информация
        user: текущий авторизованный пользователь
        session: асинхронная сессия для подключения к базе данных

    Returns:
        ResultSchema: простой ответ, что подписка удалена успешно
    """
    await delete_follower_by_id(idx=idx, user_id=user.id, session=session)

    return ResultSchema
