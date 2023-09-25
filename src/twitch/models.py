from sqlalchemy import BigInteger, ForeignKey, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, relationship, mapped_column, Mapped

from application.models import DefaultFields


class Base(DeclarativeBase):
    pass


class UserSubscription(Base):
    __tablename__ = "user_subscription"

    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), primary_key=True)
    twitch_db_user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("twitch_users.id"), primary_key=True)
    twitch_user_id: Mapped[int] = mapped_column(BigInteger)



class TwitchUser(DefaultFields, Base):
    __tablename__ = "twitch_users"

    twitch_user_id: Mapped[int] = mapped_column(BigInteger, default=0, unique=True, nullable=False)
    login: Mapped[str] = mapped_column(String, nullable=True)
    display_name: Mapped[str] = mapped_column(String)
    type: Mapped[str] = mapped_column(String)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    view_count: Mapped[int] = mapped_column(Integer, default=0)
    email: Mapped[str] = mapped_column(String, nullable=True)
    broadcaster_type: Mapped[str] = mapped_column(String)

    subscribers = relationship('auth.models.User', secondary='user_subscription', back_populates='subscriptions')


class TwitchStream(DefaultFields, Base):
    __tablename__ = "twitch_streams"

    twitch_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("twitch_users.id"), nullable=False)
    game_id: Mapped[int] = mapped_column(Integer, ForeignKey("twitch_games.id"), nullable=True)
    stream_title: Mapped[str] = mapped_column(String)
    viewer_count: Mapped[int] = mapped_column(Integer)

    user = relationship("TwitchUser", backref='streams')
    game = relationship("TwitchGame", backref='streams')


class TwitchGame(DefaultFields, Base):
    __tablename__ = "twitch_games"

    game_name: Mapped[str] = mapped_column(String, nullable=False)
    twitch_game_id: Mapped[int] = mapped_column(BigInteger, nullable=False, unique=True)


class Tag(DefaultFields, Base):
    __tablename__ = "tags"

    tag_name: Mapped[str] = mapped_column(String, nullable=False)


class StreamTag(DefaultFields, Base):
    __tablename__ = "stream_tag"

    stream_id: Mapped[int] = mapped_column(Integer, ForeignKey("twitch_streams.id"))
    tag_id: Mapped[int] = mapped_column(Integer, ForeignKey("tags.id"))


class Notification(DefaultFields, Base):
    __tablename__ = 'notifications'

    twitch_stream_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    notification_count: Mapped[int] = mapped_column(Integer, nullable=True)


class NotificationUser(DefaultFields, Base):
    __tablename__ = 'notification_user'

    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    notification_id: Mapped[int] = mapped_column(Integer, ForeignKey('notifications.id'))