from sqlalchemy.ext.asyncio import AsyncSession

from src.tweet.crud import (
    create_tweet,
    delete_tweet_by_id,
    get_all_tweets,
    add_new_like,
    delete_like,
)


async def test_create_tweet(async_session: AsyncSession):
    tweet = {'tweet_data': 'tweet', "tweet_media_ids": []}
    tweet_id = await create_tweet(tweet=tweet, user_id=2, session=async_session)
    assert tweet_id == 2


async def test_get_all_tweets(async_session: AsyncSession):
    all_tweets = await get_all_tweets(session=async_session)
    assert len(all_tweets['tweets']) == 1


async def test_add_new_like(async_session: AsyncSession):
    await add_new_like(tweet_id=2, user_id=1, session=async_session)
    result = await get_all_tweets(session=async_session)
    assert len(result['tweets'][0]['likes']) == 1


async def test_delete_like(async_session: AsyncSession):
    await delete_like(tweet_id=2, user_id=1, session=async_session)
    result = await get_all_tweets(session=async_session)
    assert len(result['tweets'][0]['likes']) == 0


async def test_delete_tweet_by_id(async_session: AsyncSession):
    await delete_tweet_by_id(idx=2, user_id=2, session=async_session)
    tweets = await get_all_tweets(session=async_session)
    assert len(tweets['tweets']) == 0
