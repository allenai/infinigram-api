import asyncio
from itertools import islice
from typing import (
    Any,
    Iterable,
    Sequence,
)

<<<<<<< Updated upstream
import numpy as np
from infini_gram_processor import indexes
||||||| Stash base
from infini_gram_processor import indexes
=======
from infini_gram_processor import get_indexes
>>>>>>> Stashed changes
from infini_gram_processor.index_mappings import AvailableInfiniGramIndexId
from infini_gram_processor.models import (
    AttributionDocument,
    SpanRankingMethod,
)
from infini_gram_processor.models.models import (
    AttributionResponse,
)
from infini_gram_processor.processor import InfiniGramProcessor
from saq import Queue
from saq.types import SettingsDict

from src.config import get_config
from src.get_documents import get_document_requests, get_spans_with_documents

config = get_config()

queue = Queue.from_url(config.attribution_queue_url, name="infini-gram-attribution")


def __get_span_text(
    infini_gram_index: InfiniGramProcessor,
    input_token_ids: Iterable[int],
    start: int,
    stop: int,
) -> tuple[Sequence[int], str]:
    span_text_tokens = list(islice(input_token_ids, start, stop))
    span_text = infini_gram_index.decode_tokens(token_ids=span_text_tokens)

    return (span_text_tokens, span_text)


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


async def attribution_job(
    ctx: Any,
    *,
    index: str,
    input: str,
    delimiters: list[str],
    allow_spans_with_partial_words: bool,
    minimum_span_length: int,
    maximum_frequency: int,
    maximum_span_density: float,
    span_ranking_method: SpanRankingMethod,
    maximum_context_length: int,
    maximum_context_length_long: int,
    maximum_context_length_snippet: int,
    maximum_documents_per_span: int,
) -> str:
    infini_gram_index = get_indexes()[AvailableInfiniGramIndexId(index)]

    attribute_result = await asyncio.to_thread(
        infini_gram_index.attribute,
        input=input,
        delimiters=delimiters,
        allow_spans_with_partial_words=allow_spans_with_partial_words,
        minimum_span_length=minimum_span_length,
        maximum_frequency=maximum_frequency,
    )

    # Limit the density of spans, and keep the longest ones
    maximum_num_spans = int(
        np.ceil(len(attribute_result.input_token_ids) * maximum_span_density)
    )

    if span_ranking_method == SpanRankingMethod.LENGTH:
        attribute_result.spans = sorted(
            attribute_result.spans, key=lambda x: x["length"], reverse=True
        )
    elif span_ranking_method == SpanRankingMethod.UNIGRAM_LOGPROB_SUM:
        attribute_result.spans = sorted(
            attribute_result.spans,
            key=lambda x: x["unigram_logprob_sum"],
            reverse=False,
        )
    else:
        raise ValueError(f"Unknown span ranking method: {span_ranking_method}")

    attribute_result.spans = attribute_result.spans[:maximum_num_spans]
    attribute_result.spans = list(sorted(attribute_result.spans, key=lambda x: x["l"]))

    spans_with_document = get_spans_with_documents(
        infini_gram_index=infini_gram_index, attribution_response=attribute_result
    )

    document_request_by_span = get_document_requests(
        attribution_response=attribute_result,
        maximum_documents_per_span=maximum_documents_per_span,
        maximum_context_length=maximum_context_length,
    )

    documents_by_span = infini_gram_index.get_documents_by_pointers(
        document_request_by_span=document_request_by_span,
    )

    for span_with_document, documents in zip(spans_with_document, documents_by_span):
        for document in documents:
            display_length_long, needle_offset_long, text_long = cut_document(
                infini_gram_index=infini_gram_index,
                token_ids=document.token_ids,
                needle_offset=document.needle_offset,
                span_length=span_with_document.length,
                maximum_context_length=maximum_context_length_long,
            )
            display_length_snippet, needle_offset_snippet, text_snippet = cut_document(
                infini_gram_index=infini_gram_index,
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
        index=infini_gram_index.index,
        spans=spans_with_document,
        input_tokens=infini_gram_index.tokenize_to_list(input),
    ).model_dump_json()


settings = SettingsDict(
    queue=queue, functions=[("attribute", attribution_job)], concurrency=1
)
