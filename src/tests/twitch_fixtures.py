import random

import pytest_asyncio

from twitch.schemas import (
    TwitchGame,
    TwitchStream,
    TwitchUser,
)

stream_titles = [
    "The Art of Programming",
    "Data Science Insights",
    "Machine Learning Basics",
    "Web Development Masterclass",
    "Python for Beginners",
    "Deep Dive into Algorithms",
    "Cybersecurity Fundamentals",
    "Cloud Computing Essentials",
    "AI and Ethics",
    "Blockchain Revolution"
]

tags = [
    "programming",
    "data science",
    "machine learning",
    "web development",
    "python",
    "algorithms",
    "cybersecurity",
    "cloud computing",
    "artificial intelligence",
    "blockchain"
]

generated_stream_ids = []


@pytest_asyncio.fixture()
async def twitch_user_one() -> TwitchUser:
    return TwitchUser(
        twitch_user_id=11111111,
        login='twitch_user_one',
        display_name='TwitchUserOne',
        type='',
        description='Lorem Ipsum',
        view_count=0,
        broadcaster_type='partner',
        email='twitch_user_one@mail.com'
    )


@pytest_asyncio.fixture()
async def twitch_user_two() -> TwitchUser:
    return TwitchUser(
        twitch_user_id=2222222,
        login='twitch_user_two',
        display_name='TwitchUserTwo',
        type='',
        description='Lorem Ipsum',
        view_count=0,
        broadcaster_type='partner',
        email='twitch_user_two@mail.com'
    )


@pytest_asyncio.fixture()
async def twitch_game():
    return TwitchGame(
        game_name='TwitchGame',
        twitch_game_id=12121212,
    )


@pytest_asyncio.fixture()
async def random_stream(twitch_user_one: TwitchUser, twitch_user_two: TwitchUser, twitch_game: TwitchGame):
    global generated_stream_ids
    stream_id = random.randrange(100, 9999999)
    while stream_id in generated_stream_ids:
        stream_id = random.randrange(100, 9999999)
    generated_stream_ids.append(stream_id)
    return TwitchStream(
        twitch_id=stream_id,
        user=random.choice([twitch_user_two, twitch_user_one]),
        twitch_game_id=twitch_game.twitch_game_id,
        game_name=twitch_game.game_name,
        stream_title=random.choice(stream_titles),
        viewer_count=1000,
        tags=random.choices(tags, k=4),
    )
