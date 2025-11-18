from typing import Any

from infini_gram_processor.index_mappings import AvailableInfiniGramIndexId
from infinigram_api_shared.saq.queue_constants import TASK_NAME_KEY, TASK_TAG_KEY
from infinigram_api_shared.saq.queue_utils import (
    get_attribute_job_name_for_index,
    get_queue_connection_pool,
    get_queue_for_index,
)
from opentelemetry import trace
from opentelemetry.semconv.trace import SpanAttributes
from opentelemetry.trace import SpanKind
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator
from saq import Queue

from src.attribution.attribution_request import AttributionRequest
from src.config import get_config


async def connect_to_attribution_queue() -> None:
    config = get_config()
    connection_pool = get_queue_connection_pool(config.attribution_queue_url)
    await connection_pool.open()


async def disconnect_from_attribution_queue() -> None:
    config = get_config()
    connection_pool = get_queue_connection_pool(config.attribution_queue_url)
    await connection_pool.close()


def get_queue(index_id: AvailableInfiniGramIndexId) -> Queue:
    config = get_config()
    return get_queue_for_index(
        queue_url=config.attribution_queue_url,
        base_queue_name=config.attribution_queue_name,
        index_id=index_id,
    )


tracer = trace.get_tracer(get_config().application_name)


async def publish_attribution_job(
    index: AvailableInfiniGramIndexId, request: AttributionRequest, job_key: str
) -> Any:
    with tracer.start_as_current_span(
        "attribution_queue_service/publish_attribution_job",
        kind=SpanKind.PRODUCER,
        attributes={
            TASK_NAME_KEY: "attribute",
            SpanAttributes.MESSAGING_MESSAGE_ID: job_key,
            TASK_TAG_KEY: "apply_async",
            SpanAttributes.MESSAGING_SYSTEM: "saq",
            "index": index.value,
        },
    ):
        otel_context: dict[str, Any] = {}
        TraceContextTextMapPropagator().inject(otel_context)

        return await get_queue(index).apply(
            get_attribute_job_name_for_index(index),
            timeout=60,
            key=job_key,
            index=index.value,
            input=request.response,
            delimiters=request.delimiters,
            allow_spans_with_partial_words=request.allow_spans_with_partial_words,
            minimum_span_length=request.minimum_span_length,
            maximum_frequency=request.maximum_frequency,
            maximum_span_density=request.maximum_span_density,
            span_ranking_method=request.span_ranking_method,
            maximum_context_length=request.maximum_context_length,
            maximum_context_length_long=request.maximum_context_length_long,
            maximum_context_length_snippet=request.maximum_context_length_snippet,
            maximum_documents_per_span=request.maximum_documents_per_span,
            otel_context=otel_context,
        )


async def abort_attribution_job(
    job_key: str, index: AvailableInfiniGramIndexId
) -> None:
    job_to_abort = await get_queue(index).job(job_key)

    if job_to_abort is not None:
        await get_queue(index).abort(job_to_abort, "Client timeout")
