"""Модуль с моделями для описания твитов и media."""
from typing import Any

from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    Table,
)

from src.auth.models import User

BaseTweet: Any = declarative_base()


likes_table: Table = Table(
    'likes_table',
    BaseTweet.metadata,
    Column(
        'tweet_id',
        ForeignKey('tweet.id', ondelete='CASCADE'),
        primary_key=True,
    ),
    Column(
        'user_id',
        ForeignKey(User.id, ondelete='CASCADE'),
        primary_key=True,
    ),
)


class Tweet(BaseTweet):
    """Класс для описания твита."""

    __tablename__ = 'tweet'

    id = Column(Integer, primary_key=True)
    tweet_data = Column(String, nullable=False)
    owner_id = Column(Integer, ForeignKey(User.id), nullable=False)
    users_likes = relationship(
        User,
        secondary=likes_table,
        lazy='selectin',
        cascade='all, delete',
    )
    tweet_media_ids = relationship(
        'Media',
        lazy='selectin',
        cascade='all, delete',
    )


class Media(BaseTweet):
    """Класс для описания загруженного изображения для твита."""

    __tablename__ = 'media'

    id = Column(Integer, primary_key=True)
    media_path = Column(String, nullable=True)
    tweet_id = Column(Integer, ForeignKey('tweet.id', ondelete='CASCADE'))
