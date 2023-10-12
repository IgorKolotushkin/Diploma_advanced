"""Модуль для создания подключения к базе данных."""
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
    async_sessionmaker,
    AsyncEngine,
)

from src.config import get_settings, Settings

settings: Settings = get_settings()

engine: AsyncEngine = create_async_engine(settings.db_url)
async_session: async_sessionmaker[AsyncSession] = async_sessionmaker(
    engine,
    expire_on_commit=False,
    class_=AsyncSession,
)


async def get_session() -> AsyncGenerator:
    """
    Функция для получения асинхронной сессии подключения к базе данных.

    Yields:
         AsyncGenerator: асинхронная сессия
    """
    async with async_session() as session:
        yield session
