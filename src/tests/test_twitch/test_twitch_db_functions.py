import pytest

from auth.schemas import ExtendedUserScheme
from db.postgre_managers import TwitchRelationalManager
from twitch.schemas import TwitchGame, TwitchStream, TwitchUser

pytest_plugins = [
    "tests.fixtures_auth",
    "tests.fixtures_twitch",
]


@pytest.mark.asyncio
async def test_save_one_user(
    twitch_user_one: TwitchUser, twitch_user_two: TwitchUser, twitch_pgdb: TwitchRelationalManager
):
    saved_user = await twitch_pgdb.save_one_user(twitch_user_one)
    assert saved_user.twitch_user_id == twitch_user_one.twitch_user_id
    assert saved_user.login == twitch_user_one.login
    second_save = await twitch_pgdb.save_one_user(twitch_user_one)
    assert second_save.id == saved_user.id
    saved_second_used = await twitch_pgdb.save_one_user(twitch_user_two)
    assert saved_second_used.twitch_user_id == twitch_user_two.twitch_user_id
    assert saved_second_used.login == twitch_user_two.login


@pytest.mark.asyncio
async def test_save_one_game(twitch_game: TwitchGame, twitch_pgdb: TwitchRelationalManager):
    saved_game = await twitch_pgdb.save_one_game(twitch_game)
    assert saved_game.twitch_game_id == twitch_game.twitch_game_id
    assert saved_game.game_name == twitch_game.game_name
    second_save = await twitch_pgdb.save_one_game(twitch_game)
    assert second_save.id == saved_game.id


@pytest.mark.asyncio
async def test_save_one_stream(random_stream: TwitchStream, twitch_pgdb: TwitchRelationalManager):
    saved_stream = await twitch_pgdb.save_one_stream(random_stream)
    assert saved_stream.twitch_id == random_stream.twitch_id
    assert saved_stream.stream_title == random_stream.stream_title
    streamer = await twitch_pgdb.get_twitch_user(saved_stream.user.twitch_user_id)
    assert saved_stream.user.login == streamer.login


@pytest.mark.asyncio
async def test_subscriptions(
    twitch_user_one: TwitchUser,
    register_user_extended: ExtendedUserScheme,
    twitch_pgdb: TwitchRelationalManager,
):
    streamers_subscribers = await twitch_pgdb.get_users_followed_to_streamer(twitch_user_one.twitch_user_id)
    assert len(streamers_subscribers) == 0
    users_subscriptions = await twitch_pgdb.get_users_subscriptions(register_user_extended)
    assert len(users_subscriptions) == 0
    followed_users = await twitch_pgdb.get_followed_users()
    assert len(followed_users) == 0

    await twitch_pgdb.subscribe_user_to_streamer(register_user_extended, twitch_user_one.twitch_user_id)
    streamers_subscribers = await twitch_pgdb.get_users_followed_to_streamer(twitch_user_one.twitch_user_id)
    assert len(streamers_subscribers) == 1
    assert streamers_subscribers[0].id == register_user_extended.id
    users_subscriptions = await twitch_pgdb.get_users_subscriptions(register_user_extended)
    assert len(users_subscriptions) == 1
    assert users_subscriptions[0].twitch_user_id == twitch_user_one.twitch_user_id
    followed_users = await twitch_pgdb.get_followed_users()
    assert len(followed_users) == 1
    assert followed_users[0].twitch_user_id == twitch_user_one.twitch_user_id

    await twitch_pgdb.unsubscribe_user_from_streamer(register_user_extended, twitch_user_one.twitch_user_id)
    streamers_subscribers = await twitch_pgdb.get_users_followed_to_streamer(twitch_user_one.twitch_user_id)
    assert len(streamers_subscribers) == 0
    users_subscriptions = await twitch_pgdb.get_users_subscriptions(register_user_extended)
    assert len(users_subscriptions) == 0
    followed_users = await twitch_pgdb.get_followed_users()
    assert len(followed_users) == 0
