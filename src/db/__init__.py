from .database_managers import TwitchDatabaseManager
from .mongo_managers import MongoTwitchManager

twitch_db = MongoTwitchManager()


def get_twitch_database() -> TwitchDatabaseManager:
    return twitch_db
