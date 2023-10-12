"""Модуль содержащий схемы для пользователя."""
from typing import List, Optional

from pydantic import BaseModel, UUID4, EmailStr


class ApiKeySchema(BaseModel):
    """Класс-схема для ApiKey."""

    apikey: UUID4


class UserSchema(BaseModel):
    """Класс-схема для пользователя."""

    id: int
    name: str


class ResultSchema(BaseModel):
    """Класс-схема для простого ответа."""

    result: str = 'true'


class UserFollowSchema(UserSchema):
    """Расширенный класс-схема пользователя с подписчиками."""

    followers: Optional[List[UserSchema]] = []
    following: Optional[List[UserSchema]] = []


class UserMeSchema(ResultSchema):
    """Расширенный класс-схема пользователя для endpoint /users/me."""

    user: UserFollowSchema


class UserLoginSchema(BaseModel):
    """Класс-схема для валидации входящих данных.

    При входе пользователя.
    """

    email: EmailStr
    password: str


class UserRegisterSchema(UserLoginSchema):
    """Дочерний класс-схема для валидации входящих данных.

    При регистрации пользователя.
    """

    password_repeat: str
