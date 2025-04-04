from functools import lru_cache

import redis.asyncio as redis

from src.config import ConfigDependency


@lru_cache
def create_connection_pool(url: str) -> redis.ConnectionPool:
    return redis.ConnectionPool.from_url(url)


def get_redis(config: ConfigDependency) -> redis.Redis:
    redis_url = config.cache_url
    pool = create_connection_pool(redis_url)

    return redis.Redis(connection_pool=pool)
