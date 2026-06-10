import asyncio
from typing import Any

from infinigram_api_shared.saq.queue_constants import TASK_NAME_KEY, TASK_TAG_KEY
from opentelemetry import trace
from opentelemetry.semconv._incubating.attributes.messaging_attributes import (
    MESSAGING_CLIENT_ID,
    MESSAGING_MESSAGE_ID,
    MESSAGING_SYSTEM,
)
from opentelemetry.trace import SpanKind
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator

from attribution_worker.attribution_worker_context import AttributionWorkerContext
from attribution_worker.config import get_config

config = get_config()

tracer = trace.get_tracer(config.application_name)


async def count_job(
    ctx: AttributionWorkerContext,
    *,
    query: str,
    otel_context: dict[str, Any],
) -> str:
    extracted_context = TraceContextTextMapPropagator().extract(otel_context)

    with tracer.start_as_current_span(
        name="attribution-worker/count",
        kind=SpanKind.CLIENT,
        context=extracted_context,
        attributes={
            MESSAGING_SYSTEM: "saq",
            TASK_NAME_KEY: "attribute",
            TASK_TAG_KEY: "apply_async",
        },
    ) as otel_span:
        job = ctx.get("job")
        if job is not None:
            otel_span.set_attribute(MESSAGING_MESSAGE_ID, job.key)

        worker = ctx.get("worker")
        if worker is not None:
            otel_span.set_attribute(MESSAGING_CLIENT_ID, worker.id)

        infini_gram_index = ctx["infini_gram_processor"]

        count_result = await asyncio.to_thread(
            infini_gram_index.count_n_gram, query=query
        )

        return count_result.model_dump_json()
