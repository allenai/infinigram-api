from typing import Annotated, TypeAlias

from fastapi import APIRouter, Query

from src.infinigram.processor import (
    InfiniGramDocumentsResponse,
    InfiniGramProcessorDependency,
    InfiniGramRankResponse,
)

documents_router = APIRouter()

MaximumDocumentDisplayLengthType: TypeAlias = Annotated[
    int,
    Query(
        title="The maximum length in tokens of the returned document text",
        gt=0,
    ),
]


@documents_router.get("/{index}/documents/{shard}/{rank}", tags=["documents"])
def get_document_by_rank(
    shard: int,
    rank: int,
    infini_gram_processor: InfiniGramProcessorDependency,
    maximum_document_display_length: MaximumDocumentDisplayLengthType = 10,
) -> InfiniGramRankResponse:
    result = infini_gram_processor.get_document_by_rank(
        shard=shard,
        rank=rank,
        maximum_document_display_length=maximum_document_display_length,
    )

    return result


@documents_router.get("/{index}/documents/", tags=["documents"])
def search_documents(
    infini_gram_processor: InfiniGramProcessorDependency,
    search: str,
    maximum_document_display_length: MaximumDocumentDisplayLengthType = 10,
) -> InfiniGramDocumentsResponse:
    result = infini_gram_processor.search_documents(
        search, maximum_document_display_length=maximum_document_display_length
    )

    return result
