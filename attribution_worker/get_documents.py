import random

from infini_gram.models import AttributionSpan as AttributionSpanFromEngine
from infini_gram_processor.models import (
    AttributionDocument,
    AttributionSpan,
    Document,
    GetDocumentByPointerRequest,
    SpanRankingMethod,
)
from infini_gram_processor.processor import InfiniGramProcessor

from .get_span_text import get_span_text


def cut_document(
    infini_gram_index: InfiniGramProcessor,
    token_ids: list[int],
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
        token_ids = token_ids[: (needle_offset + span_length + maximum_context_length)]
    display_length = len(token_ids)
    text = infini_gram_index.decode_tokens(token_ids)
    return display_length, needle_offset, text


def get_spans_with_documents(
    infini_gram_index: InfiniGramProcessor,
    spans: list[AttributionSpanFromEngine],
    documents_by_span: list[list[Document]],
    input_token_ids: list[int],
    maximum_context_length_long: int,
    maximum_context_length_snippet: int,
) -> list[AttributionSpan]:
    spans_with_documents: list[AttributionSpan] = []
    for span, documents in zip(spans, documents_by_span):
        span_documents: list[AttributionDocument] = []
        for document in documents:
            display_length_long, needle_offset_long, text_long = cut_document(
                infini_gram_index=infini_gram_index,
                token_ids=document.token_ids,
                needle_offset=document.needle_offset,
                span_length=span["length"],
                maximum_context_length=maximum_context_length_long,
            )

            display_length_snippet, needle_offset_snippet, text_snippet = cut_document(
                infini_gram_index=infini_gram_index,
                token_ids=document.token_ids,
                needle_offset=document.needle_offset,
                span_length=span["length"],
                maximum_context_length=maximum_context_length_snippet,
            )

            span_documents.append(
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

        (span_text_tokens, span_text) = get_span_text(
            infini_gram_index=infini_gram_index,
            input_token_ids=input_token_ids,
            start=span["l"],
            stop=span["r"],
        )

        new_span_with_documents = AttributionSpan(
            left=span["l"],
            right=span["r"],
            length=span["length"],
            count=span["count"],
            unigram_logprob_sum=span["unigram_logprob_sum"],
            text=span_text,
            token_ids=span_text_tokens,
            documents=span_documents,
        )

        spans_with_documents.append(new_span_with_documents)

    return spans_with_documents


def get_document_requests(
    spans: list[AttributionSpanFromEngine],
    input_token_ids: list[int],
    maximum_documents_per_span: int,
    maximum_context_length: int,
) -> list[GetDocumentByPointerRequest]:
    document_request_by_span: list[GetDocumentByPointerRequest] = []
    for span in spans:
        docs = span["docs"]
        if len(docs) > maximum_documents_per_span:
            random.seed(42)  # For reproducibility
            docs = random.sample(docs, maximum_documents_per_span)
        document_request_by_span.append(
            GetDocumentByPointerRequest(
                docs=docs,
                span_ids=input_token_ids[span["l"] : span["r"]],
                needle_length=span["length"],
                maximum_context_length=maximum_context_length,
            )
        )
    return document_request_by_span


def sort_and_cap_spans(
    spans: list[AttributionSpanFromEngine],
    ranking_method: SpanRankingMethod,
    maximum_num_spans: int,
) -> list[AttributionSpanFromEngine]:
    sorted_spans: list[AttributionSpanFromEngine]

    if ranking_method == SpanRankingMethod.LENGTH:
        sorted_spans = sorted(spans, key=lambda x: x["length"], reverse=True)
    elif ranking_method == SpanRankingMethod.UNIGRAM_LOGPROB_SUM:
        sorted_spans = sorted(
            spans,
            key=lambda x: x["unigram_logprob_sum"],
            reverse=False,
        )
    else:
        raise ValueError(f"Unknown span ranking method: {ranking_method}")

    return sorted(list(sorted_spans[:maximum_num_spans]), key=lambda span: span["l"])
