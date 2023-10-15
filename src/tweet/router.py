"""Модуль с эндпоинтами для твитов."""
from typing import Annotated, Type

from fastapi import APIRouter, Depends, Security, Request, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.datastructures import FormData

from src.auth.router import get_current_user
from src.auth.schemas import UserSchema, ResultSchema
from src.config import ODD_RESPONSES
from src.database import get_session
from src.tweet.crud import (
    save_image_path,
    create_tweet,
    delete_tweet_by_id,
    add_new_like,
    get_all_tweets,
    delete_like,
)
from src.tweet.schemas import (
    TweetSchema,
    TweetResponseSchema,
    TweetAllSchema,
    MediaSchema,
)
from src.tweet.utils import save_media
from src.auth.router import api_key_header

router: APIRouter = APIRouter(
    prefix='',
    tags=['Tweet'],
    dependencies=[Security(api_key_header)],
)


@router.post(
    '/medias',
    response_model=MediaSchema,
    description='Add images in tweet',
    responses=ODD_RESPONSES,
)
async def save_image(
    request: Request,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> MediaSchema:
    """
    Endpoint для сохранения изображения.

    Args:
        request: request
        session: асинхронная сессия для работы с базой данных

    Returns:
        MediaSchema: информация о сохраненном файле
    """
    body: FormData = await request.form()
    media_file: UploadFile = body.get('file')
    file_name: str = await save_media(media_file=media_file)
    media_id: int = await save_image_path(file_name=file_name, session=session)

    return MediaSchema(media_id=media_id)


@router.get(
    '/tweets',
    response_model=TweetAllSchema,
    description='Get all tweets',
    responses=ODD_RESPONSES,
)
async def get_tweets(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> dict:
    """
    Endpoint для получения всех твитов.

    Args:
        session: асинхронная сессия для работы с базой данных

    Returns:
        dict: информация о всех твитах
    """
    return await get_all_tweets(session=session)


@router.post(
    '/tweets',
    response_model=TweetResponseSchema,
    description='Add new tweet',
    responses=ODD_RESPONSES,
)
async def add_tweet(
    tweet: TweetSchema,
    user: Annotated[UserSchema, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> TweetResponseSchema:
    """
    Endpoint для добавления твита.

    Args:
        tweet: добавляемый твит
        user: создатель твита
        session: асинхронная сессия для работы с базой данных

    Returns:
        TweetResponseSchema: информация о сохраненном твите
    """
    tweet_id: int = await create_tweet(
        tweet=tweet.model_dump(), user_id=user.id, session=session,
    )

    return TweetResponseSchema(tweet_id=tweet_id)


@router.delete(
    '/tweets/{idx}',
    response_model=ResultSchema,
    description='Delete tweet by id',
    responses=ODD_RESPONSES,
)
async def delete_tweet(
    idx: int,
    user: Annotated[UserSchema, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> Type[ResultSchema]:
    """
    Endpoint для удаления твита по id.

    Args:
        idx: id удаляемого твита
        user: создатель твита
        session: асинхронная сессия для работы с базой данных

    Returns:
        ResultSchema: информация с подтверждением об удалении твита
    """
    await delete_tweet_by_id(idx=idx, user_id=user.id, session=session)

    return ResultSchema


@router.post(
    '/tweets/{idx}/likes',
    response_model=ResultSchema,
    description='Add like for tweet by id',
    responses=ODD_RESPONSES,
)
async def add_like(
    idx: int,
    user: Annotated[UserSchema, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> Type[ResultSchema]:
    """
    Endpoint для добавления лайка твиту по id.

    Args:
        idx: id твита для которого предназначен лайк
        user: пользователь, автор лайка
        session: асинхронная сессия для работы с базой данных

    Returns:
        ResultSchema: информация с подверждением о добавлении лайка
    """
    await add_new_like(tweet_id=idx, user_id=user.id, session=session)

    return ResultSchema


@router.delete(
    '/tweets/{idx}/likes',
    response_model=ResultSchema,
    description='Delete like by id',
    responses=ODD_RESPONSES,
)
async def delete_user_like(
    idx: int,
    user: Annotated[UserSchema, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_session)],
):
    """
    Endpoint для удаления лайка твита по id.

    Args:
        idx: id твита для удаления лайка
        user: пользователь, удаляющий лайк
        session: асинхронная сессия для работы с базой данных

    Returns:
        ResultSchema: информация с подверждением об удалении лайка
    """
    await delete_like(tweet_id=idx, user_id=user.id, session=session)

    return ResultSchema
