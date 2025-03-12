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

    @tracer.start_as_current_span("attribution_service/cut_document")
    def cut_document(
        self,
        token_ids: List[int],
        needle_offset: int,
        span_length: int,
        maximum_context_length: int,
    ) -> tuple[int, int, str]:
        # cut the left context if necessary
        if needle_offset > maximum_context_length:
            token_ids = token_ids[(needle_offset - maximum_context_length) :]
            needle_offset = maximum_context_length
        # cut the right context if necessary
        if len(token_ids) - needle_offset - span_length > maximum_context_length:
            token_ids = token_ids[
                : (needle_offset + span_length + maximum_context_length)
            ]
        display_length = len(token_ids)
        text = self.infini_gram_processor.decode_tokens(token_ids)
        return display_length, needle_offset, text

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
        maximum_context_length_long: int,
        maximum_context_length_snippet: int,
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
            spans_with_document: List[AttributionSpan] = []
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
                spans_with_document.append(span_with_document)

            document_request_by_span = []
            for span in attribute_result.spans:
                docs = span["docs"]
                if len(docs) > maximum_documents_per_span:
                    random.seed(42)  # For reproducibility
                    docs = random.sample(docs, maximum_documents_per_span)
                document_request_by_span.append(
                    GetDocumentByPointerRequest(
                        docs=docs,
                        span_ids=attribute_result.input_token_ids[span["l"]:span["r"]],
                        needle_length=span["length"],
                        maximum_context_length=maximum_context_length,
                    )
                )

            documents_by_span = self.infini_gram_processor.get_documents_by_pointers(
                document_request_by_span=document_request_by_span,
            )

            for (span_with_document, documents) in zip(spans_with_document, documents_by_span):
                for document in documents:
                    display_length_long, needle_offset_long, text_long = self.cut_document(
                        token_ids=document.token_ids,
                        needle_offset=document.needle_offset,
                        span_length=span_with_document.length,
                        maximum_context_length=maximum_context_length_long,
                    )
                    display_length_snippet, needle_offset_snippet, text_snippet = self.cut_document(
                        token_ids=document.token_ids,
                        needle_offset=document.needle_offset,
                        span_length=span_with_document.length,
                        maximum_context_length=maximum_context_length_snippet,
                    )
                    span_with_document.documents.append(
                        AttributionDocument(
                            **vars(document),
                            display_length_long=display_length_long,
                            needle_offset_long=needle_offset_long,
                            text_long=text_long,
                            display_offset_snippet=display_length_snippet,
                            needle_offset_snippet=needle_offset_snippet,
                            text_snippet=text_snippet,
                        )
                    )

            return AttributionResponse(
                index=self.infini_gram_processor.index,
                spans=spans_with_document,
                input_tokens=self.infini_gram_processor.tokenize_to_list(response),
            )
