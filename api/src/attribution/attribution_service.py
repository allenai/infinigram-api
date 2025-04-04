import logging
from hashlib import sha256
from typing import List, Optional, Sequence
from uuid import uuid4

from infini_gram_processor.models import (
    BaseInfiniGramResponse,
    Document,
)
from infini_gram_processor.processor import (
    InfiniGramProcessor,
)
from opentelemetry import trace
from pydantic import Field, ValidationError
from redis.asyncio import Redis
from rfc9457 import StatusProblem
from saq import Queue

from src.attribution.attribution_queue_service import AttributionQueueDependency
from src.attribution.attribution_request import AttributionRequest
from src.cache import CacheDependency
from src.camel_case_model import CamelCaseModel
from src.config import get_config
from src.documents.documents_router import DocumentsServiceDependency
from src.documents.documents_service import (
    DocumentsService,
)
from src.infinigram.infini_gram_dependency import InfiniGramProcessorDependency

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


class AttributionService:
    infini_gram_processor: InfiniGramProcessor
    documents_service: DocumentsService
    attribution_queue: Queue
    cache: Redis

    def __init__(
        self,
        infini_gram_processor: InfiniGramProcessorDependency,
        documents_service: DocumentsServiceDependency,
        attribution_queue: AttributionQueueDependency,
        cache: CacheDependency,
    ):
        self.infini_gram_processor = infini_gram_processor
        self.documents_service = documents_service
        self.attribution_queue = attribution_queue
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
        self, index: str, request: AttributionRequest
    ) -> AttributionResponse | None:
        key = self._get_cache_key(index, request)

        try:
            cached_json = await self.cache.get(key)

            if cached_json is None:
                return None

            cached_response = AttributionResponse.model_validate_json(cached_json)

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
        self, index: str, request: AttributionRequest, json_response: str
    ) -> None:
        key = self._get_cache_key(index, request)

        try:
            await self.cache.set(key, json_response)

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
        self, index: str, request: AttributionRequest
    ) -> AttributionResponse:
        cached_response = await self._get_cached_response(index, request)
        if cached_response is not None:
            return cached_response

        job_key = str(uuid4())

        try:
            logger.debug("Adding attribution request to queue", extra={"index": index})

            attribute_result_json = await self.attribution_queue.apply(
                "attribute",
                timeout=60,
                key=job_key,
                index=index,
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
            )

            attribute_result = AttributionResponse.model_validate_json(
                attribute_result_json
            )

            logger.debug("Adding attribution request to queue", extra={"index": index})

            await self._cache_response(index, request, attribute_result_json)

            return attribute_result
        except TimeoutError:
            logger.error(
                "Attribution request timed out",
                extra={"job_key": job_key, "index": index},
            )

            job_to_abort = await self.attribution_queue.job(job_key)
            if job_to_abort is not None:
                await self.attribution_queue.abort(job_to_abort, "Client timeout")

            raise AttributionTimeoutError(
                "The server wasn't able to process your request in time. It is likely overloaded. Please try again later."
            )
