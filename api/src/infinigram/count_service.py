import logging
from typing import Annotated, Any

from fastapi import Depends
from infini_gram_processor.index_mappings import AvailableInfiniGramIndexId
from infini_gram_processor.models.models import CountRequest
from infinigram_api_shared.saq.queue_constants import TASK_NAME_KEY, TASK_TAG_KEY
from opentelemetry import trace
from opentelemetry.semconv._incubating.attributes.messaging_attributes import (
    MESSAGING_MESSAGE_ID,
    MESSAGING_SYSTEM,
)
from opentelemetry.trace import Status, StatusCode
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator

from api.src.attribution.attribution_service import AttributionTimeoutError
from api.src.camel_case_model import CamelCaseModel
from api.src.queue_service import abort_job, get_queue

tracer = trace.get_tracer(__name__)
logger = logging.getLogger("uvicorn.error")


async def publish_count_job(
    index: AvailableInfiniGramIndexId, request: CountRequest, job_key: str
):
    with tracer.start_as_current_span(
        name="count_service/publish_count_job",
        kind=trace.SpanKind.PRODUCER,
        attributes={
            TASK_NAME_KEY: "count",
            MESSAGING_MESSAGE_ID: job_key,
            TASK_TAG_KEY: "apply_async",
            MESSAGING_SYSTEM: "saq",
            "index": index.value,
        },
    ):
        otel_context: dict[str, Any] = {}
        TraceContextTextMapPropagator().inject(otel_context)

        return await get_queue(index).apply(
            "count",
            timeout=15,
            key=job_key,
            index=index.value,
            query=request.query,
            otel_context=otel_context,
        )


class CountResponse(CamelCaseModel):
    approx: bool
    count: int


class CountService:
    @tracer.start_as_current_span("count_service/count")
    async def count(self, index: AvailableInfiniGramIndexId, request: CountRequest):
        job_key = f"count_${str(request.__hash__())}"

        try:
            logger.debug("Adding count request to queue", extra={"index": index})

            count_result_json = await publish_count_job(index, request, job_key)
            count_result = CountResponse.model_validate_json(count_result_json)

            return count_result
        except TimeoutError as ex:
            logger.error(
                "Attribution request timed out",
                extra={"job_key": job_key, "index": index},
            )

            current_span = trace.get_current_span()
            current_span.set_status(Status(StatusCode.ERROR))
            current_span.record_exception(
                ex, attributes={"job_key": job_key, "index": index.value}
            )

            await abort_job(job_key, index=index)

            raise AttributionTimeoutError(
                "The server wasn't able to process your request in time. It is likely overloaded. Please try again later."
            )


CountServiceDependency = Annotated[CountService, Depends()]
