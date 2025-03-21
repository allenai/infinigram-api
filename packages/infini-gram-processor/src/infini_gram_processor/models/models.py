from enum import Enum
from typing import Any, Optional, Sequence

from infini_gram.models import (
    AttributionDoc,
)
from infini_gram.models import (
    AttributionSpan as AttributionSpanFromEngine,
)
from pydantic import BaseModel, Field

from .camel_case_model import CamelCaseModel


class GetDocumentByRankRequest(BaseModel):
    shard: int
    rank: int
    needle_length: int
    maximum_context_length: int


class GetDocumentByPointerRequest(BaseModel):
    docs: list[AttributionDoc]
    span_ids: list[int]
    needle_length: int
    maximum_context_length: int


class GetDocumentByIndexRequest(BaseModel):
    document_index: int
    maximum_context_length: int


class SpanRankingMethod(Enum):
    LENGTH = "length"
    UNIGRAM_LOGPROB_SUM = "unigram_logprob_sum"


class BaseInfiniGramResponse(CamelCaseModel):
    index: str


class InfiniGramErrorResponse(CamelCaseModel):
    error: str


class InfiniGramCountResponse(BaseInfiniGramResponse):
    approx: bool
    count: int


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
