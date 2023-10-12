"""Модуль с моделями для описания пользователя."""
from datetime import datetime
from typing import Any

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Table,
    text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base, relationship

BaseAuth: Any = declarative_base()

followers: Table = Table(
    'followers',
    BaseAuth.metadata,
    Column('user_id', Integer, ForeignKey('user.id')),
    Column('following_id', Integer, ForeignKey('user.id')),
)


class User(BaseAuth):
    """Дочерний класс для описания пользователя."""

    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    registered_at = Column(DateTime, default=datetime.utcnow())
    all_followers = relationship(
        'User',
        secondary=followers,
        primaryjoin=(followers.c.following_id == id),
        secondaryjoin=(followers.c.user_id == id),
        back_populates='all_following',
        lazy='selectin',
    )
    all_following = relationship(
        'User',
        secondary=followers,
        primaryjoin=(followers.c.user_id == id),
        secondaryjoin=(followers.c.following_id == id),
        back_populates='all_followers',
        lazy='selectin',
    )

    def to_json(self) -> dict:
        """
        Метод для конвертации данных из базы в json.

        Returns:
            dict: информация о пользователе из базы данных
        """
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
            if column.name in {'id', 'name'}
        }


class ApiKey(BaseAuth):
    """Дочерний класс для описания ApiKey пользователя."""

    __tablename__ = 'api_key'

    id = Column(Integer, primary_key=True)
    apikey = Column(
        UUID(as_uuid=False),
        server_default=text('uuid_generate_v4()'),
        unique=True,
        nullable=False,
        index=True,
    )  # CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
    user_id = Column(Integer, ForeignKey('user.id'))
