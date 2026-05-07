from functools import lru_cache

from infini_gram_processor.index_mappings import AvailableInfiniGramIndexId
from saq import Queue

_BASE_JOB_NAME = "attribute"


def get_attribute_job_name_for_index(index_id: AvailableInfiniGramIndexId) -> str:
    return _BASE_JOB_NAME


def get_queue_name(index_id: AvailableInfiniGramIndexId, base_queue_name: str) -> str:
    return f"${base_queue_name}_${index_id.value}"


@lru_cache
def get_queue_for_index(
    queue_url: str,
    base_queue_name: str,
    index_id: AvailableInfiniGramIndexId,
    *,
) -> Queue:
    queue_name = get_queue_name(index_id, base_queue_name)
    return Queue.from_url(queue_url, name=queue_name)
