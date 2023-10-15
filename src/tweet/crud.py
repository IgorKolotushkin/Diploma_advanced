"""Модуль для работы с базой данных(tweet, likes)."""
from typing import Any, Optional

from fastapi import HTTPException, status
from sqlalchemy import (
    insert,
    delete,
    and_,
    update,
    select,
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.auth.models import User
from src.tweet.models import Media
from src.tweet.models import Tweet, likes_table
from src.tweet.utils import delete_medias


async def save_image_path(
    file_name: str,
    session: AsyncSession,
) -> int:
    """
    Функция для добавления ссылки на image твита в базу данных.

    Args:
        file_name: название загруженного файла
        session: асинхронная сессия подключения к базе данных

    Returns:
        int: id сохраненного изображения
    """
    query: Any = (
        insert(Media).
        values(media_path='media/{file_name}'.format(file_name=file_name)).
        returning(Media.id)
    )
    media_id: Optional[int] = await session.scalar(query)
    await session.commit()

    return media_id


async def create_tweet(
    tweet: dict,
    user_id: int,
    session: AsyncSession,
) -> int | None:
    """
    Функция для добавления твита в базу данных.

    Args:
        tweet: описание твита
        user_id: id пользователя, автора твита
        session: асинхронная сессия подключения к базе данных

    Returns:
        int: id сохраненного твита
    """
    query_tweet: Any = (
        insert(Tweet).
        values(tweet_data=tweet['tweet_data'], owner_id=user_id).
        returning(Tweet.id)
    )
    tweet_id: Optional[int] = await session.scalar(query_tweet)
    for media_id in tweet['tweet_media_ids']:
        query_media: Any = (
            update(Media).
            values(tweet_id=tweet_id).
            where(Media.id == media_id)
        )
        await session.execute(query_media)
    await session.commit()

    return tweet_id


async def delete_tweet_by_id(
    idx: int,
    user_id: int,
    session: AsyncSession,
) -> None:
    """
    Функция для удаления твита из базы данных.

    Args:
        idx: id удаляемого твита
        user_id: id пользователя, автора твита
        session: асинхронная сессия подключения к базе данных

    Raises:
        HTTPException: возникает при попытке удалить отсутвующий твит
    """
    query_all_path_media: Any = select(Media).where(Media.tweet_id == idx)
    medias: Any = await session.scalars(query_all_path_media)
    exist_tweet: Optional[Any] = await session.scalar(
        select(Tweet).where(Tweet.id == idx),
    )

    if not exist_tweet:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    query_del_tweet: Any = delete(Tweet).where(
        and_(Tweet.id == idx, Tweet.owner_id == user_id),
    )
    await session.execute(query_del_tweet)
    await delete_medias(medias)
    await session.commit()


async def add_new_like(
    tweet_id: int,
    user_id: int,
    session: AsyncSession,
) -> None:
    """
    Функция для добавления лайка твиту.

    Args:
        tweet_id: id твита
        user_id: id пользователя, который добавляет лайк
        session: асинхронная сессия подключения к базе данных

    Raises:
        HTTPException: возникает при попытке лайкнуть отсутвующий твит
    """
    exist_tweet: Optional[Any] = await session.scalar(
        select(Tweet).where(Tweet.id == tweet_id),
    )
    if not exist_tweet:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    if exist_tweet.owner_id != user_id:
        query: Any = (
            likes_table.
            insert().
            values(tweet_id=tweet_id, user_id=user_id)
        )
        await session.execute(query)
        await session.commit()


async def delete_like(
    tweet_id: int,
    user_id: int,
    session: AsyncSession,
) -> None:
    """
    Функция для удаления лайка у твита.

    Args:
        tweet_id: id твита
        user_id: id пользователя, который удаляет лайк
        session: асинхронная сессия подключения к базе данных

    Raises:
        HTTPException: возникает при попытке удалить лайк отсутвующего твита
    """
    exist_tweet = await session.scalar(
        select(Tweet).where(Tweet.id == tweet_id),
    )
    if not exist_tweet:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    query: Any = likes_table.delete().where(
        and_(
            likes_table.c.tweet_id == tweet_id,
            likes_table.c.user_id == user_id,
        ),
    )
    await session.execute(query)
    await session.commit()


async def get_all_tweets(session: AsyncSession) -> dict | None:
    """
    Функция для получения всех твитов из базы данных.

    Args:
        session: асинхронная сессия подключения к базе данных

    Returns:
        dict: полная информация по всем твитам
    """
    tweets: Any = await session.scalars(
        select(Tweet).options(
            selectinload(Tweet.users_likes),
            selectinload(Tweet.tweet_media_ids),
        ),
    )
    all_tweets: list = []
    for tweet in tweets.all():
        owner: User = await session.scalar(
            select(User).where(User.id == tweet.owner_id),
        )
        all_tweets.append(create_tweet_info(tweet, owner))
        all_tweets.sort(key=lambda like: len(like['likes']), reverse=True)
    return {'result': 'true', 'tweets': all_tweets}


def create_tweet_info(tweet: Tweet, owner: User) -> dict:
    """
    Вспомогательная функция.

    Приведение твита к нужному виду и добавления дополнительной информации.

    Args:
        tweet: твит, по которому нужно получить информацию
        owner: пользователь, владелец твита

    Returns:
        dict: информация по твиту в dict формате
    """
    media_links: list = [link.media_path for link in tweet.tweet_media_ids]
    likes: list[dict] = [
        {'user_id': like.id, 'name': like.name} for like in tweet.users_likes
    ]

    return {
        'id': tweet.id,
        'content': tweet.tweet_data,
        'attachments': media_links,
        'author': owner.to_json(),
        'likes': likes,
    }
