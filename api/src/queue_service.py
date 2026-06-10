from typing import Any

from infini_gram_processor.index_mappings import AvailableInfiniGramIndexId
from infinigram_api_shared.saq.queue_constants import TASK_NAME_KEY, TASK_TAG_KEY
from infinigram_api_shared.saq.queue_utils import get_queue_for_index
from opentelemetry import trace
from opentelemetry.semconv._incubating.attributes.messaging_attributes import (
    MESSAGING_MESSAGE_ID,
    MESSAGING_SYSTEM,
)
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator
from saq import Queue

from api.src.config import get_config

tracer = trace.get_tracer(__name__)


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


async def publish_job(
    index: AvailableInfiniGramIndexId, job_key: str, task_name: str, **kwargs
):
    with tracer.start_as_current_span(
        name="count_service/publish_count_job",
        kind=trace.SpanKind.PRODUCER,
        attributes={
            TASK_NAME_KEY: task_name,
            MESSAGING_MESSAGE_ID: job_key,
            TASK_TAG_KEY: "apply_async",
            MESSAGING_SYSTEM: "saq",
            "index": index.value,
        },
    ):
        otel_context: dict[str, Any] = {}
        TraceContextTextMapPropagator().inject(otel_context)

        return await get_queue(index).apply(
            task_name,
            timeout=15,
            key=job_key,
            index=index.value,
            otel_context=otel_context,
            **kwargs,
        )
