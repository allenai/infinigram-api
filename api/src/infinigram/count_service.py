import logging
from typing import Annotated

from fastapi import Depends
from infini_gram_processor.index_mappings import AvailableInfiniGramIndexId
from infini_gram_processor.models.models import (
    CountCnfRequest,
    CountCnfResponse,
    CountRequest,
)
from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode

from api.src.attribution.attribution_service import AttributionTimeoutError
from api.src.camel_case_model import CamelCaseModel
from api.src.queue_service import abort_job, publish_job

tracer = trace.get_tracer(__name__)
logger = logging.getLogger("uvicorn.error")


class CountResponse(CamelCaseModel):
    approx: bool
    count: int


class CountService:
    @tracer.start_as_current_span("count_service/count")
    async def count(
        self, index: AvailableInfiniGramIndexId, request: CountRequest
    ) -> CountResponse:
        job_key = f"count_${str(request.__hash__())}"

        try:
            logger.debug("Adding count request to queue", extra={"index": index})

            count_result_json = await publish_job(
                index, job_key=job_key, task_name="count", query=request.query
            )
            count_result = CountResponse.model_validate_json(count_result_json)

            return count_result
        except TimeoutError as ex:
            logger.error(
                "Count request timed out",
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

    @tracer.start_as_current_span("count_service/count_cnf")
    async def count_cnf(
        self, index: AvailableInfiniGramIndexId, request: CountCnfRequest
    ) -> CountCnfResponse:
        job_key = f"count_${str(request.__hash__())}"

        try:
            logger.debug("Adding count request to queue", extra={"index": index})

            count_result_json = await publish_job(
                index=index,
                job_key=job_key,
                task_name="count_cnf",
                query=request.query,
                max_clause_freq=request.max_clause_freq,
                max_diff_tokens=request.max_diff_tokens,
            )
            count_result = CountCnfResponse.model_validate_json(count_result_json)

            return count_result
        except TimeoutError as ex:
            logger.error(
                "Count CNF request timed out",
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
