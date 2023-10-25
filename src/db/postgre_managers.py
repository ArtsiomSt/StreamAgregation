import random
from collections import Counter
from typing import Any, Optional, Union

from auth.exceptions import AuthException
from auth.models import User
from auth.schemas import ExtendedUserScheme, UserRegisterScheme, UserScheme
from auth.utils import get_hashed_password, verify_password
from fastapi import HTTPException
from sqlalchemy import and_, insert, or_, select, func, delete, update, not_
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from twitch.models import (
    Notification,
    NotificationUser,
    TwitchGame,
    TwitchStream,
    TwitchUser,
    UserSubscription,
    Tag,
    StreamTag,
)
from twitch.schemas import TwitchGame as TwitchGameScheme
from twitch.schemas import TwitchStream as TwitchStreamScheme
from twitch.schemas import TwitchUser as TwitchUserScheme
from twitch.schemas import Tag as TagScheme

from db.database import get_db_session


class RelationalManager:
    db: AsyncSession = None

    async def connect_to_database(self, session: Optional[AsyncSession] = None) -> None:
        if session is not None:
            self.db = session
            return
        self.db = await get_db_session()

    async def close_database_connection(self) -> None:
        await self.db.close()


class AuthRelationalManager(RelationalManager):
    async def save_one_user(self, user: UserRegisterScheme) -> ExtendedUserScheme:  # tested
        try:
            result = await self.db.execute(
                select(User).filter(or_(User.username == user.username, User.email == user.email))
            )
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

    async def check_credentials(self, email: str, password: str) -> ExtendedUserScheme:  # tested
        try:
            result = await self.db.execute(select(User).filter_by(email=email))
            user = result.scalars().one()
        except NoResultFound:
            raise HTTPException(status_code=400, detail="No user with such credentials")
        if verify_password(password, user.hashed_password):
            return ExtendedUserScheme(**user.__dict__)
        else:
            raise HTTPException(status_code=400, detail="No user with such credentials")

    async def get_one_user_by_email(self, email: str) -> ExtendedUserScheme:  # tested
        try:
            result = await self.db.execute(select(User).filter_by(email=email))
            user = result.scalars().one()
        except NoResultFound:
            raise AuthException("Invalid subject")
        return ExtendedUserScheme(**user.__dict__)

    async def change_user_profile(self, user: ExtendedUserScheme, new_user_data: UserScheme) -> UserScheme:  # tested
        current_user = await self.get_one_user_by_email(user.email)
        await self.db.execute(
            update(User).where(User.id == current_user.id).values(
                username=new_user_data.username,
                first_name=new_user_data.first_name,
                last_name=new_user_data.last_name
            )
        )
        await self.db.commit()
        user.id = current_user.id
        return user

    async def confirm_user_email(self, email: str) -> bool:
        await self.get_one_user_by_email(email)
        await self.db.execute(
            update(User).where(User.email == email).values(is_email_verified=True)
        )
        await self.db.commit()
        return True


class TwitchRelationalManager(RelationalManager):
    async def get_test_message(self, message: str) -> Any:
        pass

    async def save_one_stream(self, stream: TwitchStreamScheme) -> TwitchStreamScheme:  # tested
        twitch_user = await self.save_one_user(stream.user)
        twitch_game = TwitchGameScheme(game_name=stream.game_name, twitch_game_id=stream.twitch_game_id)
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
            stream_tags = await self.save_stream_tags(stream.tags)
            await self.attach_tags_to_stream(stream, stream_tags)
        return stream

    async def save_one_game(self, game: TwitchGameScheme) -> TwitchGameScheme:  # tested
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

    async def save_one_user(self, user: TwitchUserScheme) -> TwitchUserScheme:  # tested
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

    async def get_followed_users(self) -> list[TwitchUserScheme]:  # tested
        result = await self.db.execute(select(TwitchUser).join(UserSubscription).distinct())
        twitch_users = result.scalars().all()
        return [TwitchUserScheme(**user.__dict__) for user in twitch_users]

    async def get_twitch_user(self, twitch_user_id: int) -> TwitchUserScheme:  # tested
        try:
            result = await self.db.execute(select(TwitchUser).filter_by(twitch_user_id=twitch_user_id).limit(1))
            current_db_user = result.scalars().one()
        except NoResultFound:
            raise HTTPException(status_code=400, detail="No such streamer")
        return current_db_user

    async def subscribe_user_to_streamer(self, user: ExtendedUserScheme, twitch_user_id: int) -> bool:  # tested
        result = await self.db.execute(
            select(UserSubscription).filter(
                and_(UserSubscription.user_id == user.id, UserSubscription.twitch_user_id == twitch_user_id)
            )
        )
        try:
            current_subscription = result.scalars().one()
        except NoResultFound:
            current_subscription = None
        if current_subscription:
            raise HTTPException(status_code=400, detail="You are already subscribed to this streamer")
        twitch_user = await self.get_twitch_user(twitch_user_id)
        new_subscription = UserSubscription(
            user_id=user.id,
            twitch_db_user_id=twitch_user.id,
            twitch_user_id=twitch_user_id,
        )
        self.db.add(new_subscription)
        await self.db.commit()
        return True

    async def unsubscribe_user_from_streamer(self, user: ExtendedUserScheme, twitch_user_id: int) -> bool:  # tested
        result = await self.db.execute(
            select(UserSubscription).filter(
                and_(UserSubscription.user_id == user.id, UserSubscription.twitch_user_id == twitch_user_id)
            )
        )
        try:
            current_subscription = result.scalars().one()
        except NoResultFound:
            raise HTTPException(status_code=400, detail="You are not subscribed to this streamer")
        await self.db.execute(
            delete(UserSubscription).filter(
                and_(UserSubscription.user_id == user.id, UserSubscription.twitch_user_id == twitch_user_id)
            )
        )
        await self.db.commit()
        return True

    async def get_users_followed_to_streamer(self, twitch_user_id: int) -> list[ExtendedUserScheme]:  # tested
        query_subscribed_user_ids = select(UserSubscription.user_id).filter_by(twitch_user_id=twitch_user_id)
        result = await self.db.execute(select(User).where(User.id.in_(query_subscribed_user_ids)))
        users_followed_to_this_streamer = result.scalars().all()
        return [ExtendedUserScheme(**user.__dict__) for user in users_followed_to_this_streamer]

    async def save_notifications(self, notified_users: list[ExtendedUserScheme], stream: TwitchStreamScheme) -> None:
        result = await self.db.execute(
            insert(Notification).returning(Notification),
            [{"twitch_stream_id": stream.twitch_id, "notification_count": len(notified_users)}],
        )
        notification = result.scalars().one()
        await self.db.execute(
            insert(NotificationUser),
            [{"user_id": user.id, "notification_id": notification.id} for user in notified_users],
        )
        await self.db.commit()

    async def check_stream_notifications(self, stream: TwitchStreamScheme) -> bool:
        result = await self.db.execute(select(Notification).filter_by(twitch_stream_id=stream.twitch_id))
        stream_notification = result.scalars().all()
        if len(stream_notification) != 0:
            return True
        return False

    async def save_stream_tags(self, tags: list[str]) -> list[TagScheme]:
        if not tags:
            return []
        result = await self.db.execute(select(Tag).where(Tag.tag_name.in_(tags)))
        existing_tags = list(map(lambda tag: tag.tag_name, result.scalars().all()))
        tags_to_save = [{"tag_name": tag} for tag in tags if tag and tag not in existing_tags]
        if tags_to_save:
            await self.db.execute(insert(Tag), tags_to_save)
        result = await self.db.execute(select(Tag).where(Tag.tag_name.in_(tags)))
        return [TagScheme(**tag.__dict__) for tag in result.scalars().all()]

    async def attach_tags_to_stream(self, stream: TwitchStreamScheme, tags: list[TagScheme]) -> None:
        if tags:
            await self.db.execute(insert(StreamTag), [{"stream_id": stream.id, "tag_id": tag.id} for tag in tags])

    async def get_parsed_streams(self, paginate_by: int = 30, page_num: int = 0) -> list[TwitchStreamScheme]:
        result = await self.db.execute(
            select(TwitchStream)
            .join(TwitchUser, TwitchStream.user_id == TwitchUser.id)
            .options(joinedload(TwitchStream.user))
            .join(TwitchGame, TwitchStream.game_id == TwitchGame.id, isouter=True)
            .options(joinedload(TwitchStream.game))
            .options(joinedload(TwitchStream.tags))
            .offset(page_num * paginate_by)
            .limit(paginate_by)
        )
        streams = result.scalars().unique().all()
        return [
            TwitchStreamScheme(
                id=stream.id,
                twitch_id=stream.twitch_id,
                user=TwitchUserScheme(**stream.user.__dict__),
                twitch_game_id=stream.game.twitch_game_id if stream.game else None,
                game_name=stream.game.game_name if stream.game else None,
                stream_title=stream.stream_title,
                viewer_count=stream.viewer_count,
                tags=[tag.tag_name for tag in stream.tags],
            )
            for stream in streams
        ]

    async def get_most_popular_twitch_games(self) -> list[TwitchGameScheme]:
        games_amount = (
            select(TwitchStream.game_id.label("game_id"), func.count(TwitchStream.game_id).label("streams_amount"))
            .group_by(TwitchStream.game_id)
            .alias("f1")
        )
        best_amount_of_streams = select(func.max(games_amount.c.streams_amount))
        best_games_id = select(games_amount.c.game_id).where(games_amount.c.streams_amount == best_amount_of_streams)
        get_best_games = select(TwitchGame).where(TwitchGame.id.in_(best_games_id))
        result = await self.db.execute(get_best_games)
        return [TwitchGameScheme(**game.__dict__) for game in result.scalars().all()]

    async def get_streamers(self, paginate_by: int = 30, page_num: int = 0, search: str = '') -> list[TwitchUserScheme]:
        result = await self.db.execute(select(TwitchUser).where(
            or_(TwitchUser.display_name.like(f'%{search}%'), TwitchUser.login.like(f'%{search}%'))).offset(
            paginate_by * page_num).limit(paginate_by))
        return [
            TwitchUserScheme(**streamer.__dict__)
            for streamer in result.scalars().all()
        ]

    async def get_games(self, paginate_by: int = 30, page_num: int = 0, search: str = '') -> list[TwitchGameScheme]:
        result = await self.db.execute(select(TwitchGame).where(
            TwitchGame.game_name.like(f'%{search}%')).offset(
            paginate_by * page_num).limit(paginate_by))
        return [
            TwitchGameScheme(**game.__dict__)
            for game in result.scalars().all()
        ]

    async def get_users_subscriptions(self,
                                      user: ExtendedUserScheme,
                                      paginate_by: int = 100,
                                      page_num: int = 0,
                                      search: str = '') -> list[TwitchUserScheme]:
        result = await self.db.execute(
            select(TwitchUser)
            .join(UserSubscription, TwitchUser.id == UserSubscription.twitch_db_user_id)
            .options(joinedload(TwitchUser.subscribers))
            .where(
                and_(UserSubscription.user_id == user.id,
                     or_(TwitchUser.display_name.like(f'%{search}%'), TwitchUser.login.like(f'%{search}%'))))
            .offset(paginate_by * page_num).limit(paginate_by)
        )
        return [
            TwitchUserScheme(**streamer.__dict__)
            for streamer in result.scalars().unique().all()
        ]

    async def get_most_popular_streamers(self, streamers_amount: int = 5) -> list[TwitchUserScheme]:
        users_with_subscriptions = (
            select(TwitchUser.id.label('twitch_user_id'), func.count(TwitchUser.id).label('subscriptions_amount'))
            .join(UserSubscription, TwitchUser.id == UserSubscription.twitch_db_user_id)
            .group_by(TwitchUser.id)
        )
        ordered_by_subscribers = (
            select(users_with_subscriptions.c.twitch_user_id)
            .order_by(users_with_subscriptions.c.subscriptions_amount)
            .limit(streamers_amount)
        )
        popular_streamers = select(TwitchUser).where(TwitchUser.id.in_(ordered_by_subscribers))
        result = await self.db.execute(popular_streamers)
        return [
            TwitchUserScheme(**streamer.__dict__)
            for streamer in result.scalars().all()
        ]

    async def get_users_favourite_games(self, user: ExtendedUserScheme, target_games_amount: int = 3):
        users_subscriptions = (
            select(UserSubscription.twitch_user_id.label('twitch_user_id'))
            .where(UserSubscription.user_id == user.id)
        )
        users_subs = (await self.db.execute(users_subscriptions)).scalars().all()
        users_subs = [int(sub) for sub in users_subs]
        users_subscriptions_games = await self.get_streamers_game(users_subs)
        counted_games = Counter([game[1] for game in users_subscriptions_games])
        top_users_games = [res[0] for res in counted_games.most_common(target_games_amount)]
        result = await self.db.execute(select(TwitchGame).where(TwitchGame.id.in_(top_users_games)))
        return [TwitchGameScheme(**game.__dict__) for game in result.scalars().all()]

    async def get_streamers_game(self,
                                 target_streamers: Optional[list[int]] = None,
                                 target_games: Optional[list[TwitchGameScheme]] = None) -> list[tuple[int, int]]:
        """
        Return list of tuples [int, int] or
        tuple[StreamerId, StreamersFavouriteGameId]
        """
        twitch_user_all_games = (
            select(
                TwitchUser.id.label('id'),
                TwitchUser.twitch_user_id.label('twitch_user_id'),
                TwitchGame.id.label('game_id'),
                TwitchGame.game_name.label('game_name')
            )
            .join(TwitchStream, TwitchUser.id == TwitchStream.user_id)
            .join(TwitchGame, TwitchStream.game_id == TwitchGame.id)
        )
        if target_streamers:
            twitch_user_all_games = twitch_user_all_games.where(
                TwitchUser.twitch_user_id.in_(target_streamers)
            ).alias('user_games')
        else:
            twitch_user_all_games = twitch_user_all_games.alias('user_games')
        twitch_users_games_count = (
            select(twitch_user_all_games, func.count(twitch_user_all_games.c.game_id).label('streams_this_game'))
            .group_by(
                twitch_user_all_games.c.id,
                twitch_user_all_games.c.twitch_user_id,
                twitch_user_all_games.c.game_id,
                twitch_user_all_games.c.game_name
            ).alias('games_count_all')
        )
        streamers_favourite_game_count = (
            select(
                twitch_users_games_count.c.id.label('id'),
                twitch_users_games_count.c.twitch_user_id,
                func.max(twitch_users_games_count.c.streams_this_game).label('best_stream_count')
            )
            .group_by(
                twitch_users_games_count.c.id,
                twitch_users_games_count.c.twitch_user_id,
            )
        ).alias('games_best_counts')
        streamers_favourite_game = (
            select(twitch_users_games_count)
            .join(
                streamers_favourite_game_count,
                and_(
                    twitch_users_games_count.c.id == streamers_favourite_game_count.c.id,
                    twitch_users_games_count.c.streams_this_game == streamers_favourite_game_count.c.best_stream_count
                )
            )
        )
        result = await self.db.execute(streamers_favourite_game)
        if target_games:
            target_games_ids = [game.id for game in target_games]
            return [(res[1], res[2]) for res in result.all() if res[2] in target_games_ids]
        else:
            return [(res[1], res[2]) for res in result.all() if res[2]]

    async def get_users_recommendations(self, user: ExtendedUserScheme, recommendations_amount: int = 10):
        users_games = await self.get_users_favourite_games(user)
        streamers_with_that_game = await self.get_streamers_game(target_games=users_games)
        streamers_id_with_that_game = [res[0] for res in streamers_with_that_game]
        users_subscribed_streamers = await self.db.execute(
            select(UserSubscription.twitch_db_user_id).where(UserSubscription.user_id == 3)
        )
        result = await self.db.execute(
            select(TwitchUser)
            .where(
                and_(
                    TwitchUser.twitch_user_id.in_(streamers_id_with_that_game),
                    not_(TwitchUser.id.in_(users_subscribed_streamers.scalars().all()))
                )
            )
        )
        target_streamers = result.scalars().all()
        if recommendations_amount > len(target_streamers):
            recommendations_amount = len(target_streamers)
        result_recommendations = random.sample(target_streamers, recommendations_amount)
        return [
            TwitchUserScheme(**streamer.__dict__)
            for streamer in result_recommendations
        ]

    async def get_streamers_by_game(self,
                                    games: Union[TwitchGameScheme, list[TwitchGameScheme]],
                                    paginate_by: int = 30,
                                    page_num: int = 0) -> list[TwitchUserScheme]:
        if not isinstance(games, list):
            games = [games]
        streamers = await self.get_streamers_game(target_games=games)
        target_streamers = [el[0] for el in streamers]
        result = await self.db.execute(
            select(TwitchUser).where(TwitchUser.twitch_user_id.in_(target_streamers))
            .offset(paginate_by*page_num).limit(paginate_by)
        )
        return [
            TwitchUserScheme(**streamer.__dict__)
            for streamer in result.scalars().all()
        ]
