"""Модуль со схемами для эндпоитов с твитами."""
from typing import List, Optional

from pydantic import BaseModel

from src.auth.schemas import UserSchema, ResultSchema


class TweetSchema(BaseModel):
    """Класс для описания и валидации данных добавления твита."""

    tweet_data: str
    tweet_media_ids: Optional[List[int]]


class MediaSchema(ResultSchema, BaseModel):
    """Класс для валидации и описания загруженного изображения."""

    media_id: int


class TweetResponseSchema(ResultSchema, BaseModel):
    """Класс для валидации и описания ответа при добавлении твита."""

    tweet_id: int


class UserLikeSchema(BaseModel):
    """Класс для валидации и описания добавления лайка к твиту."""

    user_id: int
    name: str


class BaseTweetSchema(BaseModel):
    """
    Класс для валидации и описания твита.

    Полной информации по твиту.
    """

    id: int
    content: str
    attachments: Optional[List[str]] = []
    author: UserSchema
    likes: Optional[List[UserLikeSchema]] = []


class TweetAllSchema(ResultSchema, BaseModel):
    """Класс для валидации и описания всех доступных твитов."""

    tweets: List[BaseTweetSchema]
