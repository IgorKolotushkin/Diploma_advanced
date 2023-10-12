from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from tweet.models import Tweet, likes_table


async def test_add_tweet(async_client: AsyncClient, user: dict, async_session: AsyncSession):
    data = {"tweet_data": "tweet", "tweet_media_ids": []}
    response = await async_client.post("/api/tweets", json=data, headers={"api-key": user["apikey"]})
    assert response.status_code == 200
    assert response.json() == {'result': 'true', 'tweet_id': 1}

    invalid_data = {"tweet_data": "tweet"}
    response = await async_client.post("/api/tweets", json=invalid_data, headers={"api-key": user["apikey"]})
    assert response.status_code == 422
    assert response.json() == {
        'error_message': 'Field required',
        'error_type': 'missing',
        'result': 'false',
    }

    tweets = await async_session.execute(select(Tweet))
    assert len(tweets.all()) == 1


async def test_get_tweets(async_client: AsyncClient, user: dict):
    response = await async_client.get("/api/tweets", headers={"api-key": user["apikey"]})
    assert response.status_code == 200
    assert response.json()["result"] == "true"


async def test_add_like_invalid_id(async_client: AsyncClient, user: dict, async_session: AsyncSession):
    response = await async_client.post("/api/tweets/3/likes", headers={"api-key": user["apikey"]})
    assert response.status_code == 404
    assert response.json() == {
        "result": "false",
        'error_message': 'Not Found',
        'error_type': 'HTTPException'
    }

    likes = await async_session.execute(likes_table.select())
    assert len(likes.all()) == 0


async def test_add_like(async_client: AsyncClient, user: dict, async_session: AsyncSession):
    response = await async_client.post("/api/tweets/1/likes", headers={"api-key": user["apikey"]})
    assert response.status_code == 200
    assert response.json() == {"result": "true"}

    likes = await async_session.execute(likes_table.select())
    assert len(likes.all()) == 0


async def test_delete_tweet(async_client: AsyncClient, user: dict, async_session: AsyncSession):
    response_invalid_id = await async_client.delete("/api/tweets/3", headers={"api-key": user["apikey"]})
    assert response_invalid_id.status_code == 404
    assert response_invalid_id.json() == {
        'error_message': 'Not Found',
        'error_type': 'HTTPException',
        'result': 'false'
    }

    response = await async_client.delete("/api/tweets/1", headers={"api-key": user["apikey"]})
    assert response.status_code == 200
    assert response.json() == {'result': 'true'}

    likes = await async_session.execute(likes_table.select())
    assert len(likes.all()) == 0
