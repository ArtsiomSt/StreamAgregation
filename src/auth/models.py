from application.models import DefaultFields
from sqlalchemy import String, Boolean, sql
from sqlalchemy.orm import Mapped, mapped_column, relationship
from twitch.models import Base


class User(DefaultFields, Base):
    __tablename__ = "users"

    username: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    email: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    first_name: Mapped[str] = mapped_column(String, nullable=True)
    last_name: Mapped[str] = mapped_column(String, nullable=True)
    is_email_verified: Mapped[bool] = mapped_column(server_default=sql.false())

    subscriptions = relationship(
        "twitch.models.TwitchUser", secondary="user_subscription", back_populates="subscribers"
    )
