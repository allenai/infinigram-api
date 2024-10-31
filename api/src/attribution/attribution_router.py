from typing import Annotated, List

from fastapi import APIRouter, Depends
from pydantic import Field

from src.infinigram.processor import SpanRankingMethod
from src.attribution.attribution_service import (
    AttributionService,
    FilterMethod,
    FieldsConsideredForRanking,
    InfiniGramAttributionResponse,
    InfiniGramAttributionResponseWithDocuments,
)
from src.camel_case_model import CamelCaseModel

attribution_router = APIRouter()

EXAMPLE_ATTRIBUTION_PROMPT = "What is the taxi fare in Rome?"
EXAMPLE_ATTRIBUTION_RESPONSE = "Hailing a taxi in Rome is fairly easy. Expect to pay around EUR 10-15 (approx. $11.29 - $15.58) to most tourist spots. Tipping isn't common in Italy, but round up the taxi fare or leave a small tip in the event of exceptional service. car rental is an alternative, but traffic in Rome can be daunting for newbies. If you decide to rent a car, make sure you're comfortable navigating busy medieval streets."


class AttributionRequest(CamelCaseModel):
    prompt: str = Field(examples=[EXAMPLE_ATTRIBUTION_PROMPT])
    response: str = Field(examples=[EXAMPLE_ATTRIBUTION_RESPONSE])
    delimiters: List[str] = Field(
        examples=[["\n", "."]],
        default=[],
        description="Token IDs that returned spans shouldn't include",
    )
    allow_spans_with_partial_words: bool = Field(
        default=False,
        description="Setting this to False will only check for attributions that start and end with a full word",
    )
    minimum_span_length: int = Field(
        gt=0,
        default=1,
        description='The minimum length to qualify an n-gram span as "interesting"',
    )
    maximum_frequency: int = Field(
        gt=0,
        default=10,
        description='The maximum frequency that an n-gram span can have in an index for us to consider it as "interesting"',
    )
    maximum_span_density: float = Field(
        gt=0,
        default=0.05,
        description="The maximum density of spans (measured in number of spans per response token) to return in the response",
    )
    span_ranking_method: SpanRankingMethod = Field(
        default=SpanRankingMethod.LENGTH,
        description="Ranking method when capping number of spans with maximum_span_density, options are 'length' and 'unigram_logprob_sum'",
    )
    include_documents: bool = Field(
        default=False,
        description="Set this to True if you want to have the response include referenced documents along with the spans",
    )
    maximum_documents_per_span: int = Field(
        gt=0,
        default=10,
        description="The maximum number of documents to retrieve for each span; should be no larger than maximum_frequency",
    )
    maximum_document_display_length: int = Field(
        gt=0,
        default=100,
        description="The maximum length in tokens of the returned document text",
    )
    filter_method: FilterMethod = Field(
        default=FilterMethod.NONE,
        description="Filtering method for post-processing the retrieved documents, options are 'none', 'bm25'",
    )
    filter_bm25_fields_considered: FieldsConsideredForRanking = Field(
        default=FieldsConsideredForRanking.RESPONSE,
        description="The fields to consider for BM25 filtering, options are 'prompt', 'response', 'prompt|response' (concat), 'prompt+response' (sum of scores)",
    )
    filter_bm25_ratio_to_keep: float = Field(
        default=1.0,
        description="The ratio of documents to keep after filtering with BM25",
    )
    include_input_as_tokens: bool = Field(
        default=False,
        description="Set this to True if you want the response to include the input string as a list of string tokens",
    )


@attribution_router.post(path="/{index}/attribution")
def get_document_attributions(
    body: AttributionRequest,
    attribution_service: Annotated[AttributionService, Depends()],
) -> InfiniGramAttributionResponse | InfiniGramAttributionResponseWithDocuments:
    result = attribution_service.get_attribution_for_response(
        prompt=body.prompt,
        response=body.response,
        delimiters=body.delimiters,
        allow_spans_with_partial_words=body.allow_spans_with_partial_words,
        minimum_span_length=body.minimum_span_length,
        maximum_frequency=body.maximum_frequency,
        maximum_span_density=body.maximum_span_density,
        span_ranking_method=body.span_ranking_method,
        include_documents=body.include_documents,
        maximum_documents_per_span=body.maximum_documents_per_span,
        maximum_document_display_length=body.maximum_document_display_length,
        filter_method=body.filter_method,
        filter_bm25_fields_considered=body.filter_bm25_fields_considered,
        filter_bm25_ratio_to_keep=body.filter_bm25_ratio_to_keep,
        include_input_as_tokens=body.include_input_as_tokens,
    )

    return result
