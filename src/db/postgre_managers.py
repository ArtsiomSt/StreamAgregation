from typing import Any

from sqlalchemy.orm import Session
from sqlalchemy.exc import NoResultFound

from db.database import DataBase, get_db_session, SessionMake
from db.database_managers import TwitchDatabaseManager
from twitch.schemas import (
    TwitchStream as TwitchStreamScheme,
    TwitchUser as TwitchUserScheme,
    TwitchGame as TwitchGameScheme,
)
from twitch.models import TwitchStream, TwitchUser, TwitchGame, Tag


class TwitchRelationalManager:
    db: Session = None

    async def connect_to_database(self):
        self.db = SessionMake()

    async def close_database_connection(self):
        self.db.close()

    async def get_test_message(self, message: str) -> Any:
        pass

    async def save_one_stream(self, stream: TwitchStreamScheme) -> TwitchStreamScheme:
        twitch_user = await self.save_one_user(stream.user)
        twitch_game = TwitchGameScheme(game_name=stream.game_name, twitch_game_id=stream.twitch_game_id)
        twitch_game = await self.save_one_game(twitch_game)
        print(stream.tags)
        try:
            current_db_stream = self.db.query(TwitchStream).filter_by(twitch_id=stream.twitch_id).one()
        except NoResultFound:
            current_db_stream = None
        if current_db_stream:
            stream.id = current_db_stream.id
        else:
            twitch_stream = TwitchStream(
                twitch_id=stream.twitch_id,
                user_id=twitch_user.id,
                game_id=twitch_game.id,
                stream_title=stream.stream_title,
                viewer_count=stream.viewer_count,
            )
            self.db.add(twitch_stream)
            self.db.commit()
            self.db.refresh(twitch_stream)
            stream.id = twitch_stream.id
        return stream

    async def save_one_game(self, game: TwitchGameScheme) -> TwitchGameScheme:
        try:
            current_db_game = self.db.query(TwitchGame).filter_by(twitch_game_id=game.twitch_game_id).one()
        except NoResultFound:
            current_db_game = None
        if current_db_game:
            game.id = current_db_game.id
            self.db.query(TwitchGame).filter_by(twitch_game_id=game.twitch_game_id).update(game.model_dump())
            self.db.commit()
        else:
            twitch_game = TwitchGame(
                **game.model_dump()
            )
            self.db.add(twitch_game)
            self.db.commit()
            self.db.refresh(twitch_game)
            game.id = twitch_game.id
        return game

    async def save_one_user(self, user: TwitchUserScheme) -> TwitchUserScheme:
        try:
            current_db_user = self.db.query(TwitchUser).filter_by(twitch_user_id=user.twitch_user_id).one()
        except NoResultFound:
            current_db_user = None
        if current_db_user:
            user.id = current_db_user.id
            self.db.query(TwitchUser).filter_by(twitch_user_id=user.twitch_user_id).update(user.model_dump())
            self.db.commit()
        else:
            twitch_user = TwitchUser(
                **user.model_dump()
            )
            self.db.add(twitch_user)
            self.db.commit()
            self.db.refresh(twitch_user)
            user.id = twitch_user.id
        return user
