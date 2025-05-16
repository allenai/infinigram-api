from typing import Annotated, TypeAlias

from fastapi import APIRouter, Depends, Query
from infini_gram_processor.models import GetDocumentByIndexRequest

from src.documents.documents_service import (
    DocumentsService,
    InfiniGramDocumentResponse,
    InfiniGramDocumentsResponse,
    SearchResponse,
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


@documents_router.get("/{index}/documents/", tags=["documents"])
def search_documents(
    documents_service: DocumentsServiceDependency,
    search: str,
    maximum_document_display_length: MaximumDocumentDisplayLengthType = 10,
    page: Annotated[
        int,
        Query(
            title="The page of documents to retrieve from the search query. Uses the pageSize parameter as part of its calculations. Starts at 0.",
        ),
    ] = 0,
    page_size: Annotated[
        int,
        Query(
            title="The number of documents to return from the query. Defaults to 10. Changing this will affect the documents you get from a specific page.",
            gt=0,
        ),
    ] = 10,
) -> SearchResponse:
    result = documents_service.search_documents(
        search,
        maximum_context_length=maximum_document_display_length,
        page=page,
        page_size=page_size,
    )

    return result


@documents_router.get("/{index}/get_document_by_rank/{shard}/{rank}", tags=["documents"])
def get_document_by_rank(
    documents_service: DocumentsServiceDependency,
    shard: int,
    rank: int,
    needle_length: int,
    maximum_document_display_length: MaximumDocumentDisplayLengthType = 10,
) -> InfiniGramDocumentResponse:
    result = documents_service.get_document_by_rank(
        shard=shard,
        rank=rank,
        needle_length=needle_length,
        maximum_context_length=maximum_document_display_length,
    )

    return result


@documents_router.get("/{index}/get_document_by_pointer/{shard}/{pointer}", tags=["documents"])
def get_document_by_pointer(
    documents_service: DocumentsServiceDependency,
    shard: int,
    pointer: int,
    needle_length: int,
    maximum_document_display_length: MaximumDocumentDisplayLengthType = 10,
) -> InfiniGramDocumentResponse:
    result = documents_service.get_document_by_pointer(
        shard=shard,
        pointer=pointer,
        needle_length=needle_length,
        maximum_context_length=maximum_document_display_length,
    )

    return result


@documents_router.get("/{index}/get_document_by_index/{document_index}", tags=["documents"])
def get_document_by_index(
    documents_service: DocumentsServiceDependency,
    document_index: int,
    maximum_document_display_length: MaximumDocumentDisplayLengthType = 10,
) -> InfiniGramDocumentResponse:
    result = documents_service.get_document_by_index(
        document_index=int(document_index),
        maximum_context_length=maximum_document_display_length,
    )

    return result


@documents_router.get("/{index}/get_documents_by_index", tags=["documents"])
def get_documents_by_index(
    documents_service: DocumentsServiceDependency,
    document_indexes: Annotated[list[int], Query()],
    maximum_document_display_length: MaximumDocumentDisplayLengthType = 10,
) -> InfiniGramDocumentsResponse:
    result = documents_service.get_multiple_documents_by_index(
        document_requests=[
            GetDocumentByIndexRequest(
                document_index=document_index,
                maximum_context_length=maximum_document_display_length,
            )
            for document_index in document_indexes
        ],
    )

    return result
