"""Модуль с функциями для работы с базой данных для эндпоинтов пользователя."""
from re import match
from typing import Any, Optional

from fastapi import HTTPException, status
from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.auth.models import ApiKey, User, followers
from src.auth.schemas import UserRegisterSchema
from src.auth.utils_user import hash_password



async def get_user_by_email(email: str, session: AsyncSession) -> User:
    """
    Функция для получения пользователя из базы данных по email.

    Args:
        email: email пользователя
        session: сессия подключения к базе данных

    Returns:
        User: пользователь полученный из базы данных
    """
    query: Any = select(User).filter(User.email == email)

    return await session.scalar(query)


async def create_user_apikey(user_id: int, session: AsyncSession) -> str:
    """
    Функция генерации apikey для пользователя при регистрации.

    Args:
        user_id: id пользователя
        session: сессия подключения к базе данных

    Returns:
        str: сгенерированный apikey пользователя
    """
    query: Any = insert(ApiKey).values(user_id=user_id).returning(ApiKey)
    api_key: str = await session.scalar(query)
    await session.commit()

    return api_key


async def get_user_apikey(user_id: int, session: AsyncSession) -> ApiKey:
    """
    Получение текущего пользователя из базы данных по его apikey.

    Args:
        user_id: id пользователя
        session: сессия подключения к базе данных

    Returns:
        ApiKey: apikey из базы данных для текущего пользователя
    """
    query: Any = select(ApiKey).where(ApiKey.user_id == user_id)

    return await session.scalar(query)


async def create_user(
    user: UserRegisterSchema,
    session: AsyncSession,
) -> ApiKey:
    """
    Функция создания пользователя при регистрации.

    Args:
        user: данные пользователя для регистрации
        session: сессия подключения к базе данных

    Returns:
        ApiKey: сгенерированный apikey для зарегистрированного пользователя
    """
    hashed_password: str = hash_password(user.password)
    username = match(r'\w*', user.email)
    query: Any = (
        insert(User).
        values(
            email=user.email,
            name=username.group(0),
            password=hashed_password,
        ).
        returning(User.id)
    )
    user_id: int = await session.scalar(query)
    await create_user_apikey(user_id=user_id, session=session)
    await session.commit()

    return await get_user_apikey(user_id=user_id, session=session)


async def get_user_by_apikey(apikey: str, session: AsyncSession) -> User:
    """
    Функция получения пользователя из базы данных по его ApiKey.

    Args:
        apikey: apikey текущего пользователя полученный из headers
        session: сессия подключения к базе данных

    Returns:
        User: текущий пользователь полученный из базы данных
    """
    query: Any = select(User).join(ApiKey).where(ApiKey.apikey == apikey)

    return await session.scalar(query)


async def get_all_info_user(
    user_id: int,
    session: AsyncSession,
) -> dict:
    """
    Функция получения всей информации о пользователе из базы данных по его id.

    Args:
        user_id: id пользователя
        session: сессия подключения к базе данных

    Returns:
        dict: словарь с информацией о запрошенном пользователе
        None: если пользователя нет в базе данных

    Raises:
        HTTPException: если пользователя нет в базе данных
    """
    query: Any = (
        select(User).
        where(User.id == user_id).
        options(
            selectinload(User.all_followers),
            selectinload(User.all_following),
        )
    )
    user_info: Optional[User] = await session.scalar(query)
    if not user_info:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    all_followers: list = [
        follower.to_json() for follower in user_info.all_followers
    ]
    all_following: list = [
        following.to_json() for following in user_info.all_following
    ]
    user: dict = user_info.to_json()

    return {
        'id': user['id'],
        'name': user['name'],
        'followers': all_followers,
        'following': all_following,
    }


async def delete_follower_by_id(
    idx: int,
    user_id: int,
    session: AsyncSession,
) -> None:
    """
    Функция удаления подписки на другого пользователя.

    Args:
        idx: id пользователя, подписку на которого хотим удалить
        user_id: id текущего пользователя
        session: сессия подключения к базе данных

    Raises:
        HTTPException: если текущий пользователь не подписан на пользователя,
        от которого хочет отписаться
    """
    follower: Optional[Any] = await session.scalar(
        followers.select().where(
            followers.c.user_id == user_id, followers.c.following_id == idx,
        ),
    )
    if not follower:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    await session.execute(
        followers.delete().where(
            followers.c.user_id == user_id,
            followers.c.following_id == idx,
        ),
    )
    await session.commit()


async def add_follower_by_id(
    idx: int,
    user_id: int,
    session: AsyncSession,
) -> None:
    """
    Функция добавления подписки на другого пользователя.

    Args:
        idx: id пользователя, подписку на которого хотим добавить
        user_id: id текущего пользователя
        session: сессия подключения к базе данных

    Raises:
        HTTPException: если текущий пользователь уже подписан на пользователя,
        на которого хочет подписаться
    """
    follower: Optional[Any] = await session.scalar(
        followers.select().where(
            followers.c.user_id == user_id, followers.c.following_id == idx,
        ),
    )
    if follower:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='You are already subscribed',
        )

    await session.execute(
        followers.insert().values(user_id=user_id, following_id=idx),
    )
    await session.commit()
