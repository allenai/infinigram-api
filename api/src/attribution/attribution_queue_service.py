from typing import Annotated

from fastapi import Depends
from saq import Queue

from src.config import get_config

queue = Queue.from_url(
    get_config().attribution_queue_url, name=get_config().attribution_queue_name
)


async def connect_to_attribution_queue() -> None:
    await queue.connect()


async def disconnect_from_attribution_queue() -> None:
    await queue.disconnect()


def get_queue() -> Queue:
    return queue


AttributionQueueDependency = Annotated[Queue, Depends(get_queue)]
