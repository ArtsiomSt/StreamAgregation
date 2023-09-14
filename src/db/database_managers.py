from abc import abstractmethod
from typing import Any, Protocol

from twitch.schemas import TwitchStream, TwitchUser


class DatabaseManager(Protocol):
    @property
    def client(self):
        raise NotImplementedError

    @property
    def db(self):
        raise NotImplementedError

    @abstractmethod
    async def connect_to_database(self, path: str, db_name: str):
        """Implementing db connect"""

    @abstractmethod
    async def close_database_connection(self):
        """Implementing closing db connection"""

    @abstractmethod
    async def get_test_message(self, message: str) -> Any:
        """This function is made for personal purposes and tests"""


class TwitchDatabaseManager(DatabaseManager):
    @abstractmethod
    async def save_one_user(self, user: TwitchUser) -> str:
        """Implementing saving of user"""

    @abstractmethod
    async def save_one_stream(self, stream: TwitchStream) -> str:
        """Implementing saving stream"""

    @abstractmethod
    async def get_users_by_filter(
        self,
        query_filter: dict,
        paginate_by: int | None = None,
        page_num: int | None = None,
    ) -> list[TwitchUser]:
        """Implementing of getting users from parsed streams"""
