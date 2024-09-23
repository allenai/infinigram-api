from typing import Annotated, List

from fastapi import APIRouter, Depends
from pydantic import Field

from src.attribution.attribution_service import (
    AttributionService,
    InfiniGramAttributionResponse,
    InfiniGramAttributionResponseWithDocuments,
)
from src.camel_case_model import CamelCaseModel

attribution_router = APIRouter()

EXAMPLE_ATTRIBUTION_QUERY = "Hailing a taxi in Rome is fairly easy. Expect to pay around EUR 10-15 (approx. $11.29 - $15.58) to most tourist spots. Tipping isn't common in Italy, but round up the taxi fare or leave a small tip in the event of exceptional service. car rental is an alternative, but traffic in Rome can be daunting for newbies. If you decide to rent a car, make sure you're comfortable navigating busy medieval streets."


class AttributionRequest(CamelCaseModel):
    query: str = Field(examples=[EXAMPLE_ATTRIBUTION_QUERY])
    delimiters: List[str] = Field(
        examples=[["\n", "."]],
        default=[],
        description="Token IDs that returned spans shouldn't include",
    )
    maximum_span_density: float = Field(
        gt=0,
        default=0.05,
        description="The maximum density of spans (measured in number of spans per response token) to return in the response",
    )
    minimum_span_length: int = Field(
        gt=0,
        default=5,
        description='The minimum length to qualify an n-gram span as "interesting"',
    )
    maximum_frequency: int = Field(
        gt=0,
        default=10,
        description='The maximum frequency that an n-gram span can have in an index for us to consider it as "interesting"',
    )
    include_documents: bool = Field(
        default=False,
        description="Set this to True if you want to have the response include referenced documents along with the spans",
    )
    maximum_document_display_length: int = Field(
        gt=0,
        default=100,
        description="The maximum length in tokens of the returned document text",
    )
    include_input_as_tokens: bool = Field(
        default=False,
        description="Set this to True if you want the response to include the input string as a list of string tokens",
    )
    allow_spans_with_partial_words: bool = Field(
        default=False,
        description="Setting this to False will only check for attributions that start and end with a full word",
    )
    filter_method: str = Field(
        default='none',
        description="Filtering method for post-processing the retrieved documents, options are 'none', 'bm25'",
    )
    filter_bm25_ratio_to_keep: float = Field(
        default=0.27,
        description="The ratio of documents to keep after filtering with BM25",
    )


@attribution_router.post(path="/{index}/attribution")
async def get_document_attributions(
    body: AttributionRequest,
    attribution_service: Annotated[AttributionService, Depends()],
) -> InfiniGramAttributionResponse | InfiniGramAttributionResponseWithDocuments:
    result = await attribution_service.get_attribution_for_response(
        prompt_response=body.query,
        delimiters=body.delimiters,
        maximum_span_density=body.maximum_span_density,
        minimum_span_length=body.minimum_span_length,
        maximum_frequency=body.maximum_frequency,
        include_documents=body.include_documents,
        maximum_document_display_length=body.maximum_document_display_length,
        include_input_as_tokens=body.include_input_as_tokens,
        allow_spans_with_partial_words=body.allow_spans_with_partial_words,
        filter_method=body.filter_method,
        filter_bm25_ratio_to_keep=body.filter_bm25_ratio_to_keep,
    )

    return result
