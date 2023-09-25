from sqlalchemy import String
from sqlalchemy.orm import relationship, mapped_column, Mapped

from twitch.models import Base
from application.models import DefaultFields


class User(DefaultFields, Base):
    __tablename__ = "users"

    username: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    email: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    first_name: Mapped[str] = mapped_column(String, nullable=True)
    last_name: Mapped[str] = mapped_column(String, nullable=True)

    subscriptions = relationship('twitch.models.TwitchUser', secondary='user_subscription', back_populates='subscribers')