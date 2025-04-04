from typing import Annotated

from fastapi import Depends
from redis.asyncio import Redis

from src.cache.redis import get_redis

CacheDependency = Annotated[Redis, Depends(get_redis)]
