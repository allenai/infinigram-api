from typing import Annotated, TypeAlias

from fastapi import APIRouter, Depends, Query

from src.documents.documents_service import (
    DocumentsService,
    InfiniGramDocumentResponse,
    InfiniGramDocumentsResponse,
)

documents_router = APIRouter()

MaximumDocumentDisplayLengthType: TypeAlias = Annotated[
    int,
    Query(
        title="The maximum length in tokens of the returned document text",
        gt=0,
    ),
]

DocumentsServiceDependency: TypeAlias = Annotated[DocumentsService, Depends()]


@documents_router.get("/{index}/documents/{shard}/{rank}", tags=["documents"])
def get_document_by_rank(
    shard: int,
    rank: int,
    documents_service: DocumentsServiceDependency,
    maximum_document_display_length: MaximumDocumentDisplayLengthType = 10,
) -> InfiniGramDocumentResponse:
    result = documents_service.get_document_by_rank(
        shard=shard,
        rank=rank,
        maximum_document_display_length=maximum_document_display_length,
    )

    return result


@documents_router.get("/{index}/documents/", tags=["documents"])
def search_documents(
    documents_service: DocumentsServiceDependency,
    search: str,
    maximum_document_display_length: MaximumDocumentDisplayLengthType = 10,
) -> InfiniGramDocumentsResponse:
    result = documents_service.search_documents(
        search, maximum_document_display_length=maximum_document_display_length
    )

    return result


@documents_router.get("/{index}/documents/{document_index}", tags=["documents"])
def get_document_by_index(
    documents_service: DocumentsServiceDependency,
    document_index: int,
    maximum_document_display_length: MaximumDocumentDisplayLengthType = 10,
) -> InfiniGramDocumentResponse:
    result = documents_service.get_document_by_index(
        document_index=int(document_index),
        maximum_document_display_length=maximum_document_display_length,
    )

    return result


@documents_router.get("/{index}/documents", tags=["documents"])
async def get_documents_by_index(
    documents_service: DocumentsServiceDependency,
    document_indexes: Annotated[list[int], Query()],
    maximum_document_display_length: MaximumDocumentDisplayLengthType = 10,
) -> InfiniGramDocumentsResponse:
    result = await documents_service.get_multiple_documents_by_index(
        document_indexes=document_indexes,
        maximum_document_display_length=maximum_document_display_length,
    )

    return result
