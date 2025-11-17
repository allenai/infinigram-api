import logging
from hashlib import sha256
from typing import List, Optional, Sequence
from uuid import uuid4

from infini_gram_processor.index_mappings import AvailableInfiniGramIndexId
from infini_gram_processor.models import (
    BaseInfiniGramResponse,
    Document,
)
from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode
from pydantic import Field, ValidationError
from redis.asyncio import Redis
from rfc9457 import StatusProblem

from src.attribution.attribution_queue_service import (
    abort_attribution_job,
    publish_attribution_job,
)
from src.attribution.attribution_request import AttributionRequest
from src.cache import CacheDependency
from src.camel_case_model import CamelCaseModel
from src.config import get_config

tracer = trace.get_tracer(get_config().application_name)
logger = logging.getLogger("uvicorn.error")


class AttributionDocument(Document):
    display_length_long: int
    needle_offset_long: int
    text_long: str
    display_offset_snippet: int
    needle_offset_snippet: int
    text_snippet: str


class AttributionSpan(CamelCaseModel):
    left: int
    right: int
    length: int
    count: int
    unigram_logprob_sum: float
    text: str
    token_ids: Sequence[int]
    documents: List[AttributionDocument]


class AttributionResponse(BaseInfiniGramResponse):
    spans: Sequence[AttributionSpan]
    input_tokens: Optional[Sequence[str]] = Field(
        examples=[["busy", " medieval", " streets", "."]]
    )


class AttributionTimeoutError(StatusProblem):
    type_ = "server-overloaded"
    title = "Server overloaded"
    status = 503


_CACHE_EXPIRATION_TIME = 43_200


class AttributionService:
    cache: Redis

    def __init__(
        self,
        cache: CacheDependency,
    ):
        self.cache = cache

    def _get_cache_key(self, index: str, request: AttributionRequest) -> bytes:
        combined_index_and_request = (
            f"{request.__class__.__qualname__}::{index}{request.model_dump_json()}"
        )
        key = sha256(
            combined_index_and_request.encode("utf-8", errors="ignore")
        ).digest()

        return key

    @tracer.start_as_current_span("attribution_service/_get_cached_response")
    async def _get_cached_response(
        self, index: AvailableInfiniGramIndexId, request: AttributionRequest
    ) -> AttributionResponse | None:
        key = self._get_cache_key(index.value, request)

        try:
            # Since someone asked for this again, we should keep it around longer
            # This sets it to expire after 12 hours
            cached_json = await self.cache.getex(key, ex=_CACHE_EXPIRATION_TIME)

            if cached_json is None:
                return None

            cached_response = AttributionResponse.model_validate_json(cached_json)

            current_span = trace.get_current_span()
            current_span.add_event("retrieved-cached-attribution-response")
            logger.debug(
                "Retrieved cached attribution response",
            )

            return cached_response

        except ValidationError:
            logger.error(
                "Failed to parse cached response",
                extra={"key": key.decode("utf-8")},
                exc_info=True,
            )
        except Exception:
            logger.error(
                "Failed to retrieve cached response",
                exc_info=True,
            )

        return None

    @tracer.start_as_current_span("attribution_service/_cache_response")
    async def _cache_response(
        self,
        index: AvailableInfiniGramIndexId,
        request: AttributionRequest,
        json_response: str,
    ) -> None:
        key = self._get_cache_key(index.value, request)

        try:
            # save the response and expire it after an hour
            await self.cache.set(key, json_response, ex=3_600)

            current_span = trace.get_current_span()
            current_span.add_event("cached-attribution-response")
            logger.debug(
                "Saved attribution response to cache",
            )
        except Exception:
            logger.warning(
                "Failed to cache attribution response",
                exc_info=True,
            )
            pass

    @tracer.start_as_current_span("attribution_service/get_attribution_for_response")
    async def get_attribution_for_response(
        self, index: AvailableInfiniGramIndexId, request: AttributionRequest
    ) -> AttributionResponse:
        cached_response = await self._get_cached_response(index, request)
        if cached_response is not None:
            return cached_response

        job_key = str(uuid4())

        try:
            logger.debug("Adding attribution request to queue", extra={"index": index})

            attribute_result_json = await publish_attribution_job(
                index, request, job_key=job_key
            )
            attribute_result = AttributionResponse.model_validate_json(
                attribute_result_json
            )

            await self._cache_response(index, request, attribute_result_json)

            return attribute_result
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

            await abort_attribution_job(job_key)

            raise AttributionTimeoutError(
                "The server wasn't able to process your request in time. It is likely overloaded. Please try again later."
            )
