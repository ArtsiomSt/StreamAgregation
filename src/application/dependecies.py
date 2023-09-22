from .cache import RedisCacheManager

cache_manager = RedisCacheManager()


def get_cache_manager() -> RedisCacheManager:
    return cache_manager
