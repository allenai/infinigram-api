from enum import StrEnum
from typing import Any, Optional, Sequence, Tuple, List

from infini_gram.models import (
    AttributionDoc,
)
from infini_gram.models import (
    AttributionSpan as AttributionSpanFromEngine,
)
from pydantic import BaseModel, Field

from .camel_case_model import CamelCaseModel


class InfiniGramFindRequest(CamelCaseModel):
    query: str | List[int]


class InfiniGramFindCnfRequest(CamelCaseModel):
    query: str | List[List[List[int]]]
    max_clause_freq: Optional[int] = None
    max_diff_tokens: Optional[int] = None


class InfiniGramCountRequest(CamelCaseModel):
    query: str | List[int]


class InfiniGramCountCnfRequest(CamelCaseModel):
    query: str | List[List[List[int]]]
    max_clause_freq: Optional[int] = None
    max_diff_tokens: Optional[int] = None


class InfiniGramProbRequest(CamelCaseModel):
    query: str | List[int]


class InfiniGramNtdRequest(CamelCaseModel):
    query: str | List[int]
    max_support: Optional[int] = None


class InfiniGramInfgramProbRequest(CamelCaseModel):
    query: str | List[int]


class InfiniGramInfgramNtdRequest(CamelCaseModel):
    query: str | List[int]
    max_support: Optional[int] = None


class GetDocumentByRankRequest(BaseModel):
    shard: int
    rank: int
    needle_length: int
    maximum_context_length: int


class GetDocumentByPointerRequest(BaseModel):
    shard: int
    pointer: int
    needle_length: int
    maximum_context_length: int


class GetDocumentByPointerGroupedRequest(BaseModel):
    docs: list[AttributionDoc]
    span_ids: list[int]
    needle_length: int
    maximum_context_length: int


class GetDocumentByIndexRequest(BaseModel):
    document_index: int
    maximum_context_length: int


class SpanRankingMethod(StrEnum):
    LENGTH = "length"
    UNIGRAM_LOGPROB_SUM = "unigram_logprob_sum"


class BaseInfiniGramResponse(CamelCaseModel):
    index: str


class InfiniGramErrorResponse(CamelCaseModel):
    error: str


class FindResponse(BaseInfiniGramResponse):
    cnt: int
    segment_by_shard: List[Tuple[int, int]]
    token_ids: List[int]
    tokens: List[str]


class FindCnfResponse(BaseInfiniGramResponse):
    cnt: int
    approx: bool
    ptrs_by_shard: List[List[int]]
    token_ids: List[List[List[int]]]
    tokens: List[List[List[str]]]


class CountResponse(BaseInfiniGramResponse):
    count: int
    approx: bool
    token_ids: List[int]
    tokens: List[str]


class CountCnfResponse(BaseInfiniGramResponse):
    count: int
    approx: bool
    token_ids: List[List[List[int]]]
    tokens: List[List[List[str]]]


class ProbResponse(BaseInfiniGramResponse):
    prompt_cnt: int
    cont_cnt: int
    prob: float
    token_ids: List[int]
    tokens: List[str]


class DistTokenResult(CamelCaseModel):
    cont_cnt: int
    prob: float
    token: str


class NtdResponse(BaseInfiniGramResponse):
    prompt_cnt: int
    result_by_token_id: dict[int, DistTokenResult]
    approx: bool
    token_ids: List[int]
    tokens: List[str]


class InfgramProbResponse(ProbResponse):
    suffix_len: int
    longest_suffix: str


class InfgramNtdResponse(NtdResponse):
    suffix_len: int
    longest_suffix: str


class Document(CamelCaseModel):
    document_index: int = Field(validation_alias="doc_ix")
    document_length: int = Field(validation_alias="doc_len")
    display_length: int = Field(validation_alias="disp_len")
    needle_offset: int = Field(validation_alias="needle_offset")
    metadata: dict[str, Any]
    token_ids: list[int]
    text: str
    blocked: bool = False


class InfiniGramAttributionResponse(BaseInfiniGramResponse):
    spans: list[AttributionSpanFromEngine]
    input_token_ids: list[int]


class InfiniGramSearchResponse(CamelCaseModel):
    documents: list[Document]
    total_documents: int


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
    documents: list[AttributionDocument]


class AttributionResponse(BaseInfiniGramResponse):
    spans: Sequence[AttributionSpan]
    input_tokens: Optional[Sequence[str]] = Field(
        examples=[["busy", " medieval", " streets", "."]]
    )
