import asyncio
from typing import Any

import numpy as np
from infini_gram_processor.models import (
    SpanRankingMethod,
)
from infini_gram_processor.models.models import (
    AttributionResponse,
    AttributionSpan,
)
from infinigram_api_shared.saq.queue_constants import TASK_NAME_KEY, TASK_TAG_KEY
from opentelemetry import trace
from opentelemetry.semconv.trace import SpanAttributes
from opentelemetry.trace import SpanKind
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator

from attribution_worker.attribution_worker_context import AttributionWorkerContext
from attribution_worker.config import get_config

from .get_documents import (
    get_document_requests,
    get_spans_with_documents,
    sort_and_cap_spans,
)

config = get_config()


tracer = trace.get_tracer(config.application_name)


async def attribution_job(
    ctx: AttributionWorkerContext,
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
    otel_context: dict[str, Any],
) -> str:
    extracted_context = TraceContextTextMapPropagator().extract(carrier=otel_context)

    with tracer.start_as_current_span(
        "attribution-worker/attribute",
        kind=SpanKind.CLIENT,
        context=extracted_context,
        attributes={
            SpanAttributes.MESSAGING_SYSTEM: "saq",
            TASK_NAME_KEY: "attribute",
            TASK_TAG_KEY: "apply_async",
        },
    ) as otel_span:
        job = ctx.get("job")
        if job is not None:
            otel_span.set_attribute(SpanAttributes.MESSAGING_MESSAGE_ID, job.key)

        worker = ctx.get("worker")
        if worker is not None:
            otel_span.set_attribute(SpanAttributes.MESSAGING_CLIENT_ID, worker.id)

        infini_gram_index = ctx["infini_gram_processor"]

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

        sorted_spans = sort_and_cap_spans(
            attribute_result.spans,
            ranking_method=span_ranking_method,
            maximum_num_spans=maximum_num_spans,
        )

        document_request_by_span = get_document_requests(
            spans=sorted_spans,
            input_token_ids=attribute_result.input_token_ids,
            maximum_documents_per_span=maximum_documents_per_span,
            maximum_context_length=maximum_context_length,
        )

        documents_by_span = await asyncio.to_thread(
            infini_gram_index.get_documents_by_pointers,
            document_request_by_span=document_request_by_span,
        )

        spans_with_documents: list[AttributionSpan] = get_spans_with_documents(
            infini_gram_index=infini_gram_index,
            spans=sorted_spans,
            documents_by_span=documents_by_span,
            input_token_ids=attribute_result.input_token_ids,
            maximum_context_length_long=maximum_context_length_long,
            maximum_context_length_snippet=maximum_context_length_snippet,
        )

        response = AttributionResponse(
            index=infini_gram_index.index,
            spans=spans_with_documents,
            input_tokens=infini_gram_index.tokenize_to_list(input),
        )

        return response.model_dump_json()
