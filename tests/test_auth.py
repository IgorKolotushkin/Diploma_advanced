from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.models import User, followers


async def test_register_user(async_client: AsyncClient, async_session: AsyncSession):
    data = {"email": "example@example.com", "password": "123", "password_repeat": "123"}
    response = await async_client.post("/api/register", json=data)
    assert response.status_code == 200
    assert 'apikey' in response.json()

    response = await async_client.post("/api/register", json=data)
    assert response.json() == {
        'error_message': 'User with this email already exists',
        'error_type': 'HTTPException',
        'result': 'false'
    }

    data = {"email": "example", "password": "123", "password_repeat": "123"}
    response = await async_client.post("/api/register", json=data)
    assert response.status_code == 422
    assert response.json() == {
        'error_message': 'value is not a valid email address: The email address is '
                         'not valid. It must have exactly one @-sign.',
        'error_type': 'value_error',
        'result': 'false'
    }

    users = await async_session.execute(select(User))
    assert len(users.all()) == 1


async def test_login_user(async_client: AsyncClient):
    data = {"email": "example@example.com", "password": "123"}
    response = await async_client.post("/api/login", json=data)
    assert response.status_code == 200
    assert 'apikey' in response.json()


async def test_login_invalid_email(async_client: AsyncClient):
    invalid_data = {"email": "user123@user.com", "password": "123"}
    response = await async_client.post("/api/login", json=invalid_data)
    assert response.status_code == 404
    assert response.json() == {
        'error_message': 'Incorrect email',
        'error_type': 'HTTPException',
        'result': 'false'
    }


async def test_get_user_me_invalid_api_key(async_client: AsyncClient):
    headers = {'Content-Type': 'application/json', "api-key": "qqqqq"}
    response = await async_client.get("/api/users/me", headers=headers)
    assert response.json() == {
        'result': 'false',
        'error_type': 'HTTPException',
        'error_message': 'Invalid ApiKey'
    }


async def test_get_user_me(async_client: AsyncClient, user: dict):
    response = await async_client.get("/api/users/me", headers={"api-key": user["apikey"]})
    assert response.status_code == 200
    user_info = response.json()
    assert user_info["user"]["name"] == "user"


async def test_get_user_by_id(async_client: AsyncClient, user: dict):
    response = await async_client.get("/api/users/2", headers={"api-key": user["apikey"]})
    assert response.status_code == 200
    assert response.json() == {
        'result': 'true',
        'user': {
            'followers': [],
            'following': [],
            'id': 2,
            'name': 'user1'}
    }

    invalid_response = await async_client.get("/api/users/5", headers={"api-key": user["apikey"]})
    assert invalid_response.status_code == 404
    assert invalid_response.json() == {
        'error_message': 'Not Found',
        'error_type': 'HTTPException',
        'result': 'false'
    }


async def test_add_new_follower(async_client: AsyncClient, user: dict, async_session: AsyncSession):
    response = await async_client.post("/api/users/2/follow", headers={"api-key": user["apikey"]})
    assert response.status_code == 200
    assert response.json() == {'result': 'true'}

    follow = await async_session.execute(followers.select())
    assert len(follow.all()) == 1

    repeat_response = await async_client.post("/api/users/2/follow", headers={"api-key": user["apikey"]})
    assert repeat_response.status_code == 404
    assert repeat_response.json() == {
        'error_message': 'You are already subscribed',
        'error_type': 'HTTPException',
        'result': 'false',
    }

    follow = await async_session.execute(followers.select())
    assert len(follow.all()) == 1

    response_without_user = await async_client.post("/api/users/2/follow")
    assert response_without_user.status_code == 403
    assert response_without_user.json() == {'detail': 'Not authenticated'}


async def test_delete_follower(async_client: AsyncClient, user: dict, async_session: AsyncSession):
    response = await async_client.delete(
        "/api/users/2/follow",
        headers={"api-key": user["apikey"]}
    )
    assert response.status_code == 200
    assert response.json() == {'result': 'true'}

    follow = await async_session.execute(followers.select())
    assert len(follow.all()) == 0

    response_invalid_user_id = await async_client.delete(
        "/api/users/5/follow",
        headers={"api-key": user["apikey"]}
    )
    assert response_invalid_user_id.status_code == 404
    assert response_invalid_user_id.json() == {
        'error_message': 'Not Found',
        'error_type': 'HTTPException',
        'result': 'false'
    }
