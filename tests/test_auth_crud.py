from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.crud import (
    create_user,
    get_user_by_email,
    get_all_info_user,
    add_follower_by_id,
    delete_follower_by_id,
)
from src.auth.schemas import UserRegisterSchema


async def test_register_user_crud(async_session: AsyncSession):
    user = UserRegisterSchema(email='new_user@user.com', password='123', password_repeat='123')
    result = await create_user(user, async_session)
    assert result != ''


async def test_get_user_by_email(async_session: AsyncSession):
    user = await get_user_by_email('new_user@user.com', async_session)
    assert user.name == 'new_user'


async def test_get_all_info_user(async_session: AsyncSession):
    user_info = await get_all_info_user(user_id=4, session=async_session)
    assert user_info['name'] == 'new_user'


async def test_add_follower_by_id(async_session: AsyncSession):
    await add_follower_by_id(idx=2, user_id=3, session=async_session)
    user_info = await get_all_info_user(user_id=3, session=async_session)
    assert user_info['followers'] == []
    assert user_info['following'] == [{'id': 2, 'name': 'user1'}]


async def test_delete_follower_by_id(async_session: AsyncSession):
    await delete_follower_by_id(idx=2, user_id=3, session=async_session)
    user_info = await get_all_info_user(user_id=3, session=async_session)
    assert user_info['followers'] == []
    assert user_info['following'] == []
