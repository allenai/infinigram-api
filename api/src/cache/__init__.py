from typing import Annotated

import redis.asyncio as redis
from fastapi import Depends

from api.src.cache.redis import get_redis

CacheDependency = Annotated[redis.Redis, Depends(get_redis)]
