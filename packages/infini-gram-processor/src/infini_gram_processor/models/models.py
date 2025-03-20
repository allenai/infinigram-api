from enum import Enum
from typing import Any

from infini_gram.models import (
    AttributionDoc,
    AttributionSpan,
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
    spans: list[AttributionSpan]
    input_token_ids: list[int]


class InfiniGramSearchResponse(CamelCaseModel):
    documents: list[Document]
    total_documents: int
