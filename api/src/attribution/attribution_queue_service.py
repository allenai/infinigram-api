from typing import Annotated

from fastapi import Depends
from saq import Queue

from src.config import get_config

queue = Queue.from_url(
    get_config().attribution_queue_url, name="infini-gram-attribution"
)


async def connect_to_attribution_queue():
    await queue.connect()


async def disconnect_from_attribution_queue():
    await queue.disconnect()


def get_queue():
    return queue


AttributionQueueDependency = Annotated[Queue, Depends(get_queue)]
