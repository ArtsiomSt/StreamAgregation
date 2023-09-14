from models import DefaultFields
from sqlalchemy import Column, ForeignKey, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class TwitchUser(DefaultFields, Base):
    __tablename__ = "twitch_users"

    user_id = Column(Integer, default=0)
    login = Column(String, nullable=True)
    display_name = Column(String)
    type = Column(String)
    description = Column(Text, nullable=True)
    view_count = Column(Integer, default=0)
    email = Column(String, nullable=True)


class TwitchStream(DefaultFields, Base):
    __tablename__ = "twitch_streams"

    twitch_id = Column(Integer, default=0)
    twitch_user_id = Column(Integer, ForeignKey("twitch_users.id"), nullable=False)
    game_id = Column(Integer, ForeignKey("twitch_games.id"), nullable=True)
    stream_title = Column(String)
    viewer_count = Column(Integer)


class TwitchGame(DefaultFields, Base):
    __tablename__ = "twitch_games"

    game_name = Column(String, nullable=False)


class Tag(DefaultFields, Base):
    __tablename__ = 'tags'

    tag_name = Column(String, nullable=False)


class StreamTag(DefaultFields, Base):
    __tablename__ = 'stream_tag'

    stream_id = Column(Integer, ForeignKey("twitch_streams.id"))
    tag_id = Column(Integer, ForeignKey("tags.id"))
