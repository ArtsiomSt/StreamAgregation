from typing import Any

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection, AsyncIOMotorDatabase
from twitch.schemas import TwitchStream, TwitchUser

from .database_managers import TwitchDatabaseManager


class MongoTwitchManager(TwitchDatabaseManager):
    db: AsyncIOMotorDatabase = None
    client: AsyncIOMotorClient = None
    users_collection: AsyncIOMotorCollection = None
    streams_collection: AsyncIOMotorCollection = None
    games_collection: AsyncIOMotorCollection = None

    async def connect_to_database(self, path: str, db_name: str):
        self.client = AsyncIOMotorClient(path)
        self.db = self.client[db_name]
        self.users_collection = self.db.twitch_u
        self.streams_collection = self.db.twitch_s
        self.games_collection = self.db.twitch_g

    async def close_database_connection(self):
        self.client.close()

    async def save_one_user(self, user: TwitchUser) -> str:
        created_id = await self.users_collection.insert_one(user.dict())
        user.id = str(created_id.inserted_id)
        return str(created_id.inserted_id)

    async def get_users_by_filter(
        self,
        query_filter: dict,
        paginate_by: int | None = None,
        page_num: int | None = None,
    ) -> list[TwitchUser]:
        result_list = []
        paginator = {}
        if not (paginate_by is None or page_num is None):
            paginator["skip"] = paginate_by * page_num
            paginator["limit"] = paginate_by
        async for user in self.users_collection.find(query_filter, **paginator):
            user["id"] = user["_id"]
            result_list.append(TwitchUser(**user))
        return result_list

    async def save_one_stream(self, stream: TwitchStream) -> str:
        user = stream.user
        await self.save_one_user(user)
        created_id = await self.streams_collection.insert_one(stream.dict())
        stream.id = str(created_id.inserted_id)
        return str(created_id.inserted_id)

    async def get_test_message(self, message: str) -> Any:
        # method for my personal tests, would like to keep it for now
        return {"message": message}
