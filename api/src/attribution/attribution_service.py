from rank_bm25 import BM25Okapi
import math
from typing import List, Sequence, Optional
import numpy as np

import logging
from hashlib import sha256
from typing import Any, List, Optional, Sequence
from uuid import uuid4
from infini_gram_processor.models import (
    BaseInfiniGramResponse,
    Document,
)
from infini_gram_processor.processor import (
    InfiniGramProcessor,
)
from opentelemetry import trace
from opentelemetry.semconv.trace import SpanAttributes
from opentelemetry.trace import SpanKind, Status, StatusCode
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator
from pydantic import Field, ValidationError
from redis.asyncio import Redis
from rfc9457 import StatusProblem
from saq import Queue

from src.attribution.attribution_queue_service import AttributionQueueDependency
from src.attribution.attribution_request import AttributionRequest, FilterMethod, FieldsConsideredForRanking
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

_TASK_NAME_KEY = "saq.task_name"
_TASK_TAG_KEY = "saq.action"


class AttributionDocument(Document):
    display_length_long: int
    needle_offset_long: int
    text_long: str
    display_offset_snippet: int
    needle_offset_snippet: int
    text_snippet: str
    relevance_score: float | None = None


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
            # Since someone asked for this again, we should keep it around longer
            # This sets it to expire after 12 hours
            cached_json = await self.cache.getex(key, ex=43_200)

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
        self, index: str, request: AttributionRequest, json_response: str
    ) -> None:
        key = self._get_cache_key(index, request)

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
        self, index: str, request: AttributionRequest
    ) -> AttributionResponse:
        cached_response = await self._get_cached_response(index, request)
        if cached_response is not None:
            return cached_response

        job_key = str(uuid4())

        try:
            logger.debug("Adding attribution request to queue", extra={"index": index})

            with tracer.start_as_current_span(
                "attribution_service/publish_attribution_job",
                kind=SpanKind.PRODUCER,
                attributes={
                    _TASK_NAME_KEY: "attribute",
                    SpanAttributes.MESSAGING_MESSAGE_ID: job_key,
                    _TASK_TAG_KEY: "apply_async",
                    SpanAttributes.MESSAGING_SYSTEM: "saq",
                },
            ):
                otel_context: dict[str, Any] = {}
                TraceContextTextMapPropagator().inject(otel_context)
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
                    otel_context=otel_context,
                )

            attribute_result = AttributionResponse.model_validate_json(
                attribute_result_json
            )

            # Apply BM25 filtering on each span's documents if requested
            for span in attribute_result.spans:
                span.documents = [AttributionDocument(**doc.model_dump()) for doc in span.documents]
            attribute_result.spans = filter_spans(attribute_result.spans, request)

            # Cache the filtered response
            filtered_result_json = attribute_result.model_dump_json()
            await self._cache_response(index, request, filtered_result_json)

            return attribute_result
        except TimeoutError as ex:
            logger.error(
                "Attribution request timed out",
                extra={"job_key": job_key, "index": index},
            )

            current_span = trace.get_current_span()
            current_span.set_status(Status(StatusCode.ERROR))
            current_span.record_exception(ex)

            job_to_abort = await self.attribution_queue.job(job_key)
            if job_to_abort is not None:
                await self.attribution_queue.abort(job_to_abort, "Client timeout")

            raise AttributionTimeoutError(
                "The server wasn't able to process your request in time. It is likely overloaded. Please try again later."
            )

def filter_spans(
    spans: Sequence[AttributionSpan],
    request: AttributionRequest,
    prompt: Optional[str] = None,
) -> List[AttributionSpan]:
    if request.filter_method == FilterMethod.NONE:
        return list(spans)

    if request.filter_method == FilterMethod.BM25:
        return apply_global_bm25_filter(spans, request, prompt)

    return list(spans)


def apply_global_bm25_filter(
    spans: Sequence[AttributionSpan],
    request: AttributionRequest,
    prompt: Optional[str] = None,
) -> List[AttributionSpan]:
    """
    Apply global BM25 filtering across all span documents.
    """
    all_docs = []
    span_doc_mapping = []

    for span_idx, span in enumerate(spans):
        for doc_idx, doc in enumerate(span.documents):
            all_docs.append(doc.text)
            span_doc_mapping.append((span_idx, doc_idx))

    if not all_docs:
        return list(spans)

    tokenized_corpus = [doc.split() for doc in all_docs]
    bm25 = BM25Okapi(tokenized_corpus)

    if request.filter_bm25_fields_considered == FieldsConsideredForRanking.RESPONSE:
        query = request.response.split()
        scores_array = bm25.get_scores(query)

    elif request.filter_bm25_fields_considered == FieldsConsideredForRanking.PROMPT:
        if prompt:
            query = prompt.split()
            scores_array = bm25.get_scores(query)
        else:
            query = request.response.split()
            scores_array = bm25.get_scores(query)

    elif request.filter_bm25_fields_considered == FieldsConsideredForRanking.CONCATENATE_PROMPT_AND_RESPONSE:
        if prompt:
            query = (prompt + " " + request.response).split()
        else:
            query = request.response.split()
        scores_array = bm25.get_scores(query)

    elif request.filter_bm25_fields_considered == FieldsConsideredForRanking.ADD_PROMPT_AND_RESPONSE_SCORES:
        response_query = request.response.split()
        response_scores = bm25.get_scores(response_query)
        if prompt:
            prompt_query = prompt.split()
            prompt_scores = bm25.get_scores(prompt_query)
            scores_array = response_scores + prompt_scores
        else:
            scores_array = response_scores

    else:
        raise ValueError("Unknown BM25 fields_considered option")

    n_docs = len(all_docs)
    n_keep = math.ceil(n_docs * request.filter_bm25_ratio_to_keep)
    n_keep = max(1, min(n_keep, n_docs))

    indices_sorted = np.argsort(scores_array)[::-1]
    indices_to_keep = set(indices_sorted[:n_keep])

    # Build filtered spans
    filtered_spans = []
    doc_global_idx = 0

    for span_idx, span in enumerate(spans):
        new_docs = []
        for doc_idx, doc in enumerate(span.documents):
            if doc_global_idx in indices_to_keep:
                doc.relevance_score = float(scores_array[doc_global_idx])
                new_docs.append(doc)
                # new_docs.append(doc.model_dump())
                doc_global_idx += 1

        filtered_spans.append(
            AttributionSpan(
                left=span.left,
                right=span.right,
                length=span.length,
                count=span.count,
                unigram_logprob_sum=span.unigram_logprob_sum,
                text=span.text,
                token_ids=span.token_ids,
                documents=new_docs,
            )
        )

    return filtered_spans
