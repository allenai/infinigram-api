import random
from itertools import islice
from typing import Iterable, List, Optional, Sequence

import numpy as np
from opentelemetry import trace
from pydantic import Field

from src.camel_case_model import CamelCaseModel
from src.config import get_config
from src.documents.documents_router import DocumentsServiceDependency
from src.documents.documents_service import (
    DocumentsService,
)
from src.infinigram.processor import (
    BaseInfiniGramResponse,
    Document,
    GetDocumentByPointerRequest,
    InfiniGramProcessor,
    InfiniGramProcessorDependency,
    SpanRankingMethod,
)

tracer = trace.get_tracer(get_config().application_name)


class AttributionSpan(CamelCaseModel):
    left: int
    right: int
    length: int
    count: int
    unigram_logprob_sum: float
    text: str
    token_ids: Sequence[int]
    documents: List[Document]


class AttributionResponse(BaseInfiniGramResponse):
    spans: Sequence[AttributionSpan]
    input_tokens: Optional[Sequence[str]] = Field(
        examples=[["busy", " medieval", " streets", "."]]
    )


class AttributionService:
    infini_gram_processor: InfiniGramProcessor
    documents_service: DocumentsService

    def __init__(
        self,
        infini_gram_processor: InfiniGramProcessorDependency,
        documents_service: DocumentsServiceDependency,
    ):
        self.infini_gram_processor = infini_gram_processor
        self.documents_service = documents_service

    def __get_span_text(
        self, input_token_ids: Iterable[int], start: int, stop: int
    ) -> tuple[Sequence[int], str]:
        span_text_tokens = list(islice(input_token_ids, start, stop))
        span_text = self.infini_gram_processor.decode_tokens(token_ids=span_text_tokens)

        return (span_text_tokens, span_text)

    @tracer.start_as_current_span("attribution_service/get_attribution_for_response")
    def get_attribution_for_response(
        self,
        response: str,
        delimiters: List[str],
        allow_spans_with_partial_words: bool,
        minimum_span_length: int,
        maximum_frequency: int,
        maximum_span_density: float,
        span_ranking_method: SpanRankingMethod,
        maximum_context_length: int,
        maximum_documents_per_span: int,
    ) -> AttributionResponse:

        attribute_result = self.infini_gram_processor.attribute(
            input=response,
            delimiters=delimiters,
            allow_spans_with_partial_words=allow_spans_with_partial_words,
            minimum_span_length=minimum_span_length,
            maximum_frequency=maximum_frequency,
        )

        # Limit the density of spans, and keep the longest ones
        maximum_num_spans = int(np.ceil(len(attribute_result.input_token_ids) * maximum_span_density))
        if span_ranking_method == SpanRankingMethod.LENGTH:
            attribute_result.spans = sorted(attribute_result.spans, key=lambda x: x["length"], reverse=True)
        elif span_ranking_method == SpanRankingMethod.UNIGRAM_LOGPROB_SUM:
            attribute_result.spans = sorted(attribute_result.spans, key=lambda x: x["unigram_logprob_sum"], reverse=False)
        else:
            raise ValueError(f"Unknown span ranking method: {span_ranking_method}")
        attribute_result.spans = attribute_result.spans[:maximum_num_spans]
        attribute_result.spans = list(sorted(attribute_result.spans, key=lambda x: x["l"]))

        # Populate the spans with documents
        with tracer.start_as_current_span(
            "attribution_service/get_documents_for_spans"
        ):
            spans: List[AttributionSpan] = []
            for span in attribute_result.spans:
                (span_text_tokens, span_text) = self.__get_span_text(
                    input_token_ids=attribute_result.input_token_ids,
                    start=span["l"],
                    stop=span["r"],
                )
                span_with_document = AttributionSpan(
                    left=span["l"],
                    right=span["r"],
                    length=span["length"],
                    count=span["count"],
                    unigram_logprob_sum=span["unigram_logprob_sum"],
                    documents=[],
                    text=span_text,
                    token_ids=span_text_tokens,
                )
                spans.append(span_with_document)

            all_document_requests = []
            span_ix_of_document_requests = []
            for span_ix, span in enumerate(attribute_result.spans):
                document_requests: List[GetDocumentByPointerRequest] = [
                    GetDocumentByPointerRequest(
                        shard=document["s"],
                        pointer=document["ptr"],
                        needle_length=span["length"],
                        maximum_context_length=maximum_context_length,
                    )
                    for document in span["docs"]
                ]
                if len(document_requests) > maximum_documents_per_span:
                    random.seed(42)  # For reproducibility
                    document_requests = random.sample(
                        document_requests, maximum_documents_per_span
                    )
                all_document_requests.extend(document_requests)
                span_ix_of_document_requests.extend([span_ix] * len(document_requests))

            all_documents = self.infini_gram_processor.get_documents_by_pointers(
                document_requests=all_document_requests,
            )

            for (span_ix, document) in zip(span_ix_of_document_requests, all_documents):
                spans[span_ix].documents.append(document)

            return AttributionResponse(
                index=self.infini_gram_processor.index,
                spans=spans,
                input_tokens=self.infini_gram_processor.tokenize_to_list(response),
            )
