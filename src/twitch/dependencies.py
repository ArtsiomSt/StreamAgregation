from db.postgre_managers import TwitchRelationalManager
from .service import TwitchParser

twitch_parser = TwitchParser()


def get_twitch_parser() -> TwitchParser:
    return twitch_parser


async def get_twitch_pdb() -> TwitchRelationalManager:
    manager = TwitchRelationalManager()
    try:
        await manager.connect_to_database()
        yield manager
    finally:
        await manager.close_database_connection()
