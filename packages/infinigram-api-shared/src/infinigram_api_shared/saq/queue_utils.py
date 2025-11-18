from functools import lru_cache

from infini_gram_processor.index_mappings import AvailableInfiniGramIndexId
from psycopg_pool import AsyncConnectionPool
from saq import Queue
from saq.queue.postgres import PostgresQueue

_BASE_JOB_NAME = "attribute"


def get_attribute_job_name_for_index(index_id: AvailableInfiniGramIndexId) -> str:
    return f"${_BASE_JOB_NAME}_${index_id.value}"


@lru_cache
def get_queue_connection_pool(queue_url: str) -> AsyncConnectionPool:
    return AsyncConnectionPool(
        conninfo=queue_url, check=AsyncConnectionPool.check_connection, open=False
    )


def get_queue_name(index_id: AvailableInfiniGramIndexId, base_queue_name: str) -> str:
    return f"${base_queue_name}_${index_id.value}"


@lru_cache
def get_queue_for_index(
    queue_url: str,
    base_queue_name: str,
    index_id: AvailableInfiniGramIndexId,
    *,
    manage_pool_lifecycle: bool = False,
) -> Queue:
    connection_pool = get_queue_connection_pool(queue_url)
    queue_name = get_queue_name(index_id, base_queue_name)
    return PostgresQueue(
        pool=connection_pool,
        name=queue_name,
        manage_pool_lifecycle=manage_pool_lifecycle,
    )
