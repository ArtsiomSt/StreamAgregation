from application.models import DefaultFields
from sqlalchemy import String, sql, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from twitch.models import Base


class User(DefaultFields, Base):
    __tablename__ = "users"

    username: Mapped[str] = mapped_column(String, nullable=False, unique=False)
    email: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    first_name: Mapped[str] = mapped_column(String, nullable=True)
    last_name: Mapped[str] = mapped_column(String, nullable=True)
    is_email_verified: Mapped[bool] = mapped_column(server_default=sql.false())

    subscriptions = relationship(
        "twitch.models.TwitchUser", secondary="user_subscription", back_populates="subscribers"
    )


class AdminUsers(DefaultFields, Base):
    __tablename__ = 'admins_users'

    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, unique=True)
    is_superuser: Mapped[bool] = mapped_column(server_default=sql.false())

    user: Mapped[User] = relationship('User')

