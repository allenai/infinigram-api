import asyncio
from typing import (
    Any,
    List,
)

from infini_gram_processor import AvailableInfiniGramIndexId, indexes
from saq import Queue
from saq.types import SettingsDict

from src.config import get_config

config = get_config()

queue = Queue.from_url(config.attribution_queue_url, name="infini-gram-attribution")

index = indexes[AvailableInfiniGramIndexId.OLMO_2_0325_32B]


async def attribution_job(
    ctx: Any,
    *,
    input: str,
    delimiters: List[str],
    allow_spans_with_partial_words: bool,
    minimum_span_length: int,
    maximum_frequency: int,
):
    result = await asyncio.to_thread(
        index.attribute,
        input=input,
        delimiters=delimiters,
        allow_spans_with_partial_words=allow_spans_with_partial_words,
        minimum_span_length=minimum_span_length,
        maximum_frequency=maximum_frequency,
    )

    return result.model_dump_json()


settings = SettingsDict(
    queue=queue, functions=[("attribute", attribution_job)], concurrency=1
)
