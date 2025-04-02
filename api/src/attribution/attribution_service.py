from typing import List, Optional, Sequence
from uuid import uuid4

from infini_gram_processor.models import (
    BaseInfiniGramResponse,
    Document,
    SpanRankingMethod,
)
from infini_gram_processor.processor import (
    InfiniGramProcessor,
)
from opentelemetry import trace
from pydantic import Field
from rfc9457 import StatusProblem
from saq import Queue

from src.attribution.attribution_queue_service import AttributionQueueDependency
from src.camel_case_model import CamelCaseModel
from src.config import get_config
from src.documents.documents_router import DocumentsServiceDependency
from src.documents.documents_service import (
    DocumentsService,
)
from src.infinigram.infini_gram_dependency import InfiniGramProcessorDependency

tracer = trace.get_tracer(get_config().application_name)


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

    def __init__(
        self,
        infini_gram_processor: InfiniGramProcessorDependency,
        documents_service: DocumentsServiceDependency,
        attribution_queue: AttributionQueueDependency,
    ):
        self.infini_gram_processor = infini_gram_processor
        self.documents_service = documents_service
        self.attribution_queue = attribution_queue

    @tracer.start_as_current_span("attribution_service/get_attribution_for_response")
    async def get_attribution_for_response(
        self,
        index: str,
        response: str,
        delimiters: List[str],
        allow_spans_with_partial_words: bool,
        minimum_span_length: int,
        maximum_frequency: int,
        maximum_span_density: float,
        span_ranking_method: SpanRankingMethod,
        maximum_context_length: int,
        maximum_context_length_long: int,
        maximum_context_length_snippet: int,
        maximum_documents_per_span: int,
    ) -> AttributionResponse:
        job_key = str(uuid4())

        try:
            attribute_result_json = await self.attribution_queue.apply(
                "attribute",
                timeout=0,
                key=job_key,
                index=index,
                input=response,
                delimiters=delimiters,
                allow_spans_with_partial_words=allow_spans_with_partial_words,
                minimum_span_length=minimum_span_length,
                maximum_frequency=maximum_frequency,
                maximum_span_density=maximum_span_density,
                span_ranking_method=span_ranking_method,
                maximum_context_length=maximum_context_length,
                maximum_context_length_long=maximum_context_length_long,
                maximum_context_length_snippet=maximum_context_length_snippet,
                maximum_documents_per_span=maximum_documents_per_span,
            )

            attribute_result = AttributionResponse.model_validate_json(
                attribute_result_json
            )

            return attribute_result
        except TimeoutError:
            job_to_abort = await self.attribution_queue.job(job_key)
            if job_to_abort is not None:
                await self.attribution_queue.abort(job_to_abort, "Client timeout")

            raise AttributionTimeoutError(
                "The server wasn't able to process your request in time. It is likely overloaded. Please try again later."
            )
