from sqlalchemy import BigInteger, Column, ForeignKey, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase

from models import DefaultFields


class Base(DeclarativeBase):
    pass


class TwitchUser(DefaultFields, Base):
    __tablename__ = "twitch_users"

    twitch_user_id = Column(BigInteger, default=0, unique=True, nullable=False)
    login = Column(String, nullable=True)
    display_name = Column(String)
    type = Column(String)
    description = Column(Text, nullable=True)
    view_count = Column(Integer, default=0)
    email = Column(String, nullable=True)
    broadcaster_type = Column(String)


class TwitchStream(DefaultFields, Base):
    __tablename__ = "twitch_streams"

    twitch_id = Column(BigInteger, unique=True, nullable=False)
    user_id = Column(Integer, ForeignKey("twitch_users.id"), nullable=False)
    game_id = Column(Integer, ForeignKey("twitch_games.id"), nullable=True)
    stream_title = Column(String)
    viewer_count = Column(Integer)


class TwitchGame(DefaultFields, Base):
    __tablename__ = "twitch_games"

    game_name = Column(String, nullable=False)
    twitch_game_id = Column(BigInteger, nullable=False, unique=True)


class Tag(DefaultFields, Base):
    __tablename__ = "tags"

    tag_name = Column(String, nullable=False)


class StreamTag(DefaultFields, Base):
    __tablename__ = "stream_tag"

    stream_id = Column(Integer, ForeignKey("twitch_streams.id"))
    tag_id = Column(Integer, ForeignKey("tags.id"))
