from .service import TwitchParser

twitch_parser = TwitchParser()


def get_twitch_parser() -> TwitchParser:
    return twitch_parser
