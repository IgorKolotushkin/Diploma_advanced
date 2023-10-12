import asyncio

import pytest
from typing import AsyncGenerator

import sqlalchemy
from httpx import AsyncClient
from testcontainers.postgres import PostgresContainer
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
    async_sessionmaker,
    AsyncEngine,
)

from src.auth.models import BaseAuth
from src.database import get_session
from src.main import app_api
from src.tweet.models import BaseTweet
from src.config import get_settings

settings = get_settings()

postgres = PostgresContainer()
postgres.start()
postgres.driver = "asyncpg"

test_engine: AsyncEngine = create_async_engine(postgres.get_connection_url())
test_async_session = async_sessionmaker(
    test_engine,
    expire_on_commit=False,
    class_=AsyncSession,
    autoflush=False
)

BaseAuth.metadata.bind = test_engine
BaseTweet.metadata.bind = test_engine


async def override_get_session() -> AsyncGenerator:
    async with test_async_session() as session:
        yield session


app_api.dependency_overrides[get_session] = override_get_session


@pytest.fixture(scope="session", autouse=True)
async def setup_database():
    async with test_engine.begin() as conn:
        await conn.execute(sqlalchemy.text("create extension \"uuid-ossp\";"))
        await conn.run_sync(BaseAuth.metadata.create_all)
        await conn.run_sync(BaseTweet.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(BaseTweet.metadata.drop_all)
        await conn.run_sync(BaseAuth.metadata.drop_all)
    postgres.stop()


@pytest.fixture(scope="session")
async def user(async_client: AsyncClient):
    data = {"email": "user1@user.com", "password": "123", "password_repeat": "123"}
    await async_client.post("/api/register", json=data)
    data = {"email": "user@user.com", "password": "123", "password_repeat": "123"}
    response = await async_client.post("/api/register", json=data)
    yield response.json()


@pytest.fixture(scope="session")
def event_loop(request):
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(app=app_api, base_url="http://test") as async_client:
        yield async_client


@pytest.fixture(scope="session")
async def async_session():
    async with test_async_session() as session:
        yield session
