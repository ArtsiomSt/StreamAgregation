from sqlalchemy import Column, String
from sqlalchemy.orm import DeclarativeBase, relationship, Mapped, mapped_column

from twitch.models import Base
from models import DefaultFields


class User(DefaultFields, Base):
    __tablename__ = "users"

    username = Column(String, nullable=False, unique=True)
    email = Column(String, nullable=False, unique=True)
    hashed_password = Column(String, nullable=False)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)

    subscriptions = relationship('twitch.models.TwitchUser', secondary='user_subscription', back_populates='subscribers')