from typing import Annotated, TypeAlias

from fastapi import APIRouter, Depends, Query
from infini_gram_processor.models import (
    GetDocumentByIndexRequest,
    GetDocumentByPointerRequest,
    GetDocumentByRankRequest,
)

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


@documents_router.post("/{index}/get_document_by_rank", tags=["documents"])
def get_document_by_rank(
    documents_service: DocumentsServiceDependency,
    body: GetDocumentByRankRequest,
) -> InfiniGramDocumentResponse:
    result = documents_service.get_document_by_rank(
        shard=body.shard,
        rank=body.rank,
        needle_length=body.needle_length,
        maximum_context_length=body.maximum_context_length,
    )

    return result


@documents_router.post("/{index}/get_document_by_pointer", tags=["documents"])
def get_document_by_pointer(
    documents_service: DocumentsServiceDependency,
    body: GetDocumentByPointerRequest,
) -> InfiniGramDocumentResponse:
    result = documents_service.get_document_by_pointer(
        shard=body.shard,
        pointer=body.pointer,
        needle_length=body.needle_length,
        maximum_context_length=body.maximum_context_length,
    )

    return result


@documents_router.post("/{index}/get_document_by_index", tags=["documents"])
def get_document_by_index(
    documents_service: DocumentsServiceDependency,
    body: GetDocumentByIndexRequest,
) -> InfiniGramDocumentResponse:
    result = documents_service.get_document_by_index(
        document_index=body.document_index,
        maximum_context_length=body.maximum_context_length,
    )

    return result


@documents_router.post("/{index}/get_documents_by_index", tags=["documents"])
def get_documents_by_index(
    documents_service: DocumentsServiceDependency,
    body: list[GetDocumentByIndexRequest],
) -> InfiniGramDocumentsResponse:
    result = documents_service.get_multiple_documents_by_index(
        document_requests=body,
    )

    return result
