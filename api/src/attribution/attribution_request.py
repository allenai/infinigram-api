from typing import List
from enum import Enum
from infini_gram_processor.models import SpanRankingMethod
from pydantic import ConfigDict, Field

from src.camel_case_model import CamelCaseModel

EXAMPLE_ATTRIBUTION_RESPONSE = "Hailing a taxi in Rome is fairly easy. Expect to pay around EUR 10-15 (approx. $11.29 - $15.58) to most tourist spots. Tipping isn't common in Italy, but round up the taxi fare or leave a small tip in the event of exceptional service. car rental is an alternative, but traffic in Rome can be daunting for newbies. If you decide to rent a car, make sure you're comfortable navigating busy medieval streets."
class FilterMethod(Enum):
    NONE = "none"
    BM25 = "bm25"
class FieldsConsideredForRanking(Enum):
    PROMPT = "prompt"
    RESPONSE = "response"
    CONCATENATE_PROMPT_AND_RESPONSE = "prompt|response"
    ADD_PROMPT_AND_RESPONSE_SCORES = "prompt+response"
class AttributionRequest(CamelCaseModel):
    model_config = ConfigDict(frozen=True)

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
    maximum_documents_per_span: int = Field(
        gt=0,
        default=10,
        description="The maximum number of documents to retrieve for each span; should be no larger than maximum_frequency",
    )
    maximum_context_length: int = Field(
        gt=0,
        default=250,
        description="The maximum number of tokens of the context (on each side) to retrieve from the document",
    )
    maximum_context_length_long: int = Field(
        gt=0,
        default=100,
        description="The maximum number of tokens of the context (on each side) for the document modal",
    )
    maximum_context_length_snippet: int = Field(
        gt=0,
        default=40,
        description="The maximum number of tokens of the context (on each side) for the snippet in document cards",
    )
    
    filter_method: FilterMethod = Field(
        default=FilterMethod.NONE,
        description="Filtering method for post-processing the retrieved documents. Options: 'none', 'bm25'",
    )
    
    filter_bm25_fields_considered: FieldsConsideredForRanking = Field(
        default=FieldsConsideredForRanking.RESPONSE,
        description="Fields to consider for BM25 scoring: 'prompt', 'response', 'prompt|response', 'prompt+response'",
    )
    
    filter_bm25_ratio_to_keep: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Ratio of top-scoring documents to retain after BM25 filtering (between 0.0 and 1.0)",
    )
