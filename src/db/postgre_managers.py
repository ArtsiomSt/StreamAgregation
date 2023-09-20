from typing import Any

from fastapi import HTTPException
from sqlalchemy import or_, select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession

from auth.exceptions import AuthException
from auth.models import User
from auth.schemas import ExtendedUserScheme, UserRegisterScheme
from auth.utils import get_hashed_password, verify_password
from db.database import get_db_session
from twitch.models import TwitchGame, TwitchStream, TwitchUser
from twitch.schemas import TwitchGame as TwitchGameScheme
from twitch.schemas import TwitchStream as TwitchStreamScheme
from twitch.schemas import TwitchUser as TwitchUserScheme


class RelationalManager:
    db: AsyncSession = None

    async def connect_to_database(self) -> None:
        self.db = await get_db_session()

    async def close_database_connection(self) -> None:
        await self.db.close()


class AuthRelationalManager(RelationalManager):
    async def save_one_user(self, user: UserRegisterScheme) -> ExtendedUserScheme:
        try:
            result = await self.db.execute(select(User).filter(or_(User.username == user.username, User.email == user.email)))
            current_db_user = result.scalars().one()
        except NoResultFound:
            current_db_user = None
        if current_db_user is not None:
            detail = ""
            if current_db_user.username == user.username:
                detail += "User with such username already exists\n"
            if current_db_user.email == user.email:
                detail += "User with such email already exists\n"
            raise HTTPException(status_code=400, detail=detail)
        user_model = User(
            username=user.username,
            email=user.email,
            hashed_password=get_hashed_password(user.password),
            first_name=user.first_name,
            last_name=user.last_name,
        )
        self.db.add(user_model)
        await self.db.commit()
        await self.db.refresh(user_model)
        return ExtendedUserScheme(**user_model.__dict__)

    async def check_credentials(self, email: str, password: str) -> ExtendedUserScheme:
        try:
            result = await self.db.execute(select(User).filter_by(email=email))
            user = result.scalars().one()
        except NoResultFound:
            raise HTTPException(status_code=400, detail="No user with such credentials")
        if verify_password(password, user.hashed_password):
            return ExtendedUserScheme(**user.__dict__)
        else:
            raise HTTPException(status_code=400, detail="No user with such credentials")

    async def get_one_user_by_email(self, email: str) -> ExtendedUserScheme:
        try:
            result = await self.db.execute(select(User).filter_by(email=email))
            user = result.scalars().one()
        except NoResultFound:
            raise AuthException("Invalid token subject")
        return ExtendedUserScheme(**user.__dict__)


class TwitchRelationalManager(RelationalManager):
    async def get_test_message(self, message: str) -> Any:
        pass

    async def save_one_stream(self, stream: TwitchStreamScheme) -> TwitchStreamScheme:
        twitch_user = await self.save_one_user(stream.user)
        twitch_game = TwitchGameScheme(
            game_name=stream.game_name, twitch_game_id=stream.twitch_game_id
        )
        twitch_game = await self.save_one_game(twitch_game)
        try:
            result = await self.db.execute(select(TwitchStream).filter_by(twitch_id=stream.twitch_id))
            current_db_stream = result.scalars().one()
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
            await self.db.commit()
            await self.db.refresh(twitch_stream)
            stream.id = twitch_stream.id
        return stream

    async def save_one_game(self, game: TwitchGameScheme) -> TwitchGameScheme:
        if not game.twitch_game_id or not game.game_name:
            game.id = None
            return game
        try:
            result = await self.db.execute(select(TwitchGame).filter_by(twitch_game_id=game.twitch_game_id))
            current_db_game = result.scalars().one()
        except NoResultFound:
            current_db_game = None
        if current_db_game:
            game.id = current_db_game.id
        else:
            twitch_game = TwitchGame(**game.model_dump())
            self.db.add(twitch_game)
            await self.db.commit()
            await self.db.refresh(twitch_game)
            game.id = twitch_game.id
        return game

    async def save_one_user(self, user: TwitchUserScheme) -> TwitchUserScheme:
        try:
            result = await self.db.execute(select(TwitchUser).filter_by(twitch_user_id=user.twitch_user_id).limit(1))
            current_db_user = result.scalars().one()
        except NoResultFound:
            current_db_user = None
        if current_db_user:
            user.id = current_db_user.id
        else:
            twitch_user = TwitchUser(**user.model_dump())
            self.db.add(twitch_user)
            await self.db.commit()
            await self.db.refresh(twitch_user)
            user.id = twitch_user.id
        return user

    async def get_followed_users(self) -> list[TwitchUserScheme]:
        result = await self.db.execute(select(TwitchUser))
        twitch_users = result.scalars().all()
        return [TwitchUserScheme(**user.__dict__) for user in twitch_users]
