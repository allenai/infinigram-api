import logging
import os

from infini_gram_processor.index_mappings import AvailableInfiniGramIndexId
from infini_gram_processor.job_name import get_attribute_job_name_for_index
from infini_gram_processor.processor import InfiniGramProcessor
from infinigram_api_shared.otel.otel_setup import set_up_tracing
from saq import Queue
from saq.types import SettingsDict

from attribution_worker.attribution_worker_context import AttributionWorkerContext

from .attribution_handler import attribution_job
from .config import get_config

config = get_config()

queue = Queue.from_url(config.attribution_queue_url, name=config.attribution_queue_name)


try:
    assigned_index = os.getenv("ASSIGNED_INDEX")
    assigned_index_enum = AvailableInfiniGramIndexId(assigned_index)
except Exception as e:
    raise Exception("Invalid index ID") from e

set_up_tracing()


async def startup(ctx: AttributionWorkerContext) -> None:
    logging.getLogger().info(
        "Worker starting up for index %s", assigned_index_enum.value
    )

    ctx["infini_gram_processor"] = InfiniGramProcessor(assigned_index_enum)

    logging.getLogger().info(
        "Worker finished starting up for index %s", assigned_index_enum.value
    )


settings = SettingsDict(
    queue=queue,
    functions=[
        (get_attribute_job_name_for_index(assigned_index_enum), attribution_job)  # type: ignore[list-item] # The type for this isn't general enough to work with our fns
    ],
    startup=startup,
    concurrency=1,
)
