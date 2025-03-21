import random

from infini_gram_processor.models.models import (
    AttributionSpan,
    GetDocumentByPointerRequest,
    InfiniGramAttributionResponse,
)
from infini_gram_processor.processor import InfiniGramProcessor

from .get_span_text import get_span_text


def get_spans_with_documents(
    infini_gram_index: InfiniGramProcessor,
    attribution_response: InfiniGramAttributionResponse,
) -> list[AttributionSpan]:
    spans_with_document: list[AttributionSpan] = []
    for span in attribution_response.spans:
        (span_text_tokens, span_text) = get_span_text(
            infini_gram_index=infini_gram_index,
            input_token_ids=attribution_response.input_token_ids,
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

    return spans_with_document


def get_document_requests(
    attribution_response: InfiniGramAttributionResponse,
    maximum_documents_per_span: int,
    maximum_context_length: int,
) -> list[GetDocumentByPointerRequest]:
    document_request_by_span: list[GetDocumentByPointerRequest] = []
    for span in attribution_response.spans:
        docs = span["docs"]
        if len(docs) > maximum_documents_per_span:
            random.seed(42)  # For reproducibility
            docs = random.sample(docs, maximum_documents_per_span)
        document_request_by_span.append(
            GetDocumentByPointerRequest(
                docs=docs,
                span_ids=attribution_response.input_token_ids[span["l"] : span["r"]],
                needle_length=span["length"],
                maximum_context_length=maximum_context_length,
            )
        )
    return document_request_by_span


# def get_documents_for_spans(
#     infini_gram_index: InfiniGramProcessor,
#     attribution_response: InfiniGramAttributionResponse,
#     maximum_documents):
#     get_spans_with_documents()
