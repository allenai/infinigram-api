from infini_gram_processor.index_mappings import AvailableInfiniGramIndexId
from infinigram_api_shared.saq.queue_utils import get_queue_for_index
from saq import Queue

from api.src.config import get_config


def get_queue(index_id: AvailableInfiniGramIndexId) -> Queue:
    config = get_config()
    return get_queue_for_index(
        queue_url=config.attribution_queue_url,
        base_queue_name=config.attribution_queue_name,
        index_id=index_id,
    )


async def abort_job(job_key: str, index: AvailableInfiniGramIndexId) -> None:
    job_to_abort = await get_queue(index).job(job_key)

    if job_to_abort is not None:
        await get_queue(index).abort(job_to_abort, "Client timeout")
