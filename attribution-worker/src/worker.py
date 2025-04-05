import asyncio
from typing import (
    Any,
)

from infini_gram_processor import get_indexes
from infini_gram_processor.index_mappings import AvailableInfiniGramIndexId
from saq import Queue
from saq.types import SettingsDict
from src.config import get_config

config = get_config()

queue = Queue.from_url(config.attribution_queue_url, name="infini-gram-attribution")


async def attribution_job(
    ctx: Any,
    *,
    index: str,
    input: str,
    delimiters: list[str],
    allow_spans_with_partial_words: bool,
    minimum_span_length: int,
    maximum_frequency: int,
) -> str:
    infini_gram_index = get_indexes()[AvailableInfiniGramIndexId(index)]

    result = await asyncio.to_thread(
        infini_gram_index.attribute,
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
