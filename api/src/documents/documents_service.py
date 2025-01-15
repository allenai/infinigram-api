from math import ceil
from typing import Iterable, List

from pydantic import BaseModel

from src.infinigram.processor import (
    BaseInfiniGramResponse,
    Document,
    DocumentWithPointer,
    InfiniGramProcessor,
    InfiniGramProcessorDependency,
)


class InfiniGramDocumentResponse(Document, BaseInfiniGramResponse): ...


class InfiniGramDocumentsResponse(BaseInfiniGramResponse):
    documents: Iterable[Document]


class SearchResponse(BaseInfiniGramResponse):
    documents: List[Document]
    page: int
    page_size: int
    page_count: int
    total_documents: int


class GetDocumentByPointerRequest(BaseModel):
    shard: int
    pointer: int


class DocumentsService:
    infini_gram_processor: InfiniGramProcessor

    def __init__(self, infini_gram_processor: InfiniGramProcessorDependency):
        self.infini_gram_processor = infini_gram_processor

    def search_documents(
        self,
        search: str,
        maximum_document_display_length: int,
        page_size: int,
        page: int,
    ) -> SearchResponse:
        search_documents_result = self.infini_gram_processor.search_documents(
            search=search,
            maximum_document_display_length=maximum_document_display_length,
            page=page,
            page_size=page_size,
        )

        mapped_documents = [
            Document(
                text=document.text,
                document_index=document.document_index,
                document_length=document.document_length,
                display_length=document.display_length,
                needle_offset=document.needle_offset,
                metadata=document.metadata,
                token_ids=document.token_ids,
            )
            for document in search_documents_result.documents
        ]

        return SearchResponse(
            index=self.infini_gram_processor.index,
            documents=mapped_documents,
            page=page,
            page_size=page_size,
            total_documents=search_documents_result.total_documents,
            page_count=ceil(search_documents_result.total_documents / page_size),
        )

    def get_document_by_rank(
        self, shard: int, rank: int, maximum_document_display_length: int
    ) -> InfiniGramDocumentResponse:
        get_document_by_index_result = self.infini_gram_processor.get_document_by_rank(
            shard=shard,
            rank=rank,
            maximum_document_display_length=maximum_document_display_length,
        )

        return InfiniGramDocumentResponse(
            index=self.infini_gram_processor.index,
            text=get_document_by_index_result.text,
            document_index=get_document_by_index_result.document_index,
            document_length=get_document_by_index_result.document_length,
            display_length=get_document_by_index_result.display_length,
            needle_offset=get_document_by_index_result.needle_offset,
            metadata=get_document_by_index_result.metadata,
            token_ids=get_document_by_index_result.token_ids,
        )

    def get_document_by_index(
        self, document_index: int, maximum_document_display_length: int
    ) -> InfiniGramDocumentResponse:
        document = self.infini_gram_processor.get_document_by_index(
            document_index=document_index,
            maximum_document_display_length=maximum_document_display_length,
        )

        return InfiniGramDocumentResponse(
            index=self.infini_gram_processor.index,
            document_index=document.document_index,
            document_length=document.document_length,
            display_length=document.display_length,
            needle_offset=document.needle_offset,
            metadata=document.metadata,
            token_ids=document.token_ids,
            text=document.text,
        )

    def get_multiple_documents_by_index(
        self, document_indexes: Iterable[int], maximum_document_display_length: int
    ) -> InfiniGramDocumentsResponse:
        documents = self.infini_gram_processor.get_documents_by_indexes(
            list_of_document_index=list(document_indexes),
            maximum_document_display_length=maximum_document_display_length,
        )
        mapped_documents = [
            Document(
                document_index=document.document_index,
                document_length=document.document_length,
                display_length=document.display_length,
                needle_offset=document.needle_offset,
                metadata=document.metadata,
                token_ids=document.token_ids,
                text=document.text,
            )
            for document in documents
        ]
        return InfiniGramDocumentsResponse(
            index=self.infini_gram_processor.index, documents=mapped_documents
        )

    def get_document_by_pointer(
        self,
        document_request: GetDocumentByPointerRequest,
        maximum_document_display_length: int,
    ) -> DocumentWithPointer:
        document = self.infini_gram_processor.get_document_by_pointer(
            shard=document_request.shard,
            pointer=document_request.pointer,
            maximum_document_display_length=maximum_document_display_length,
        )

        return DocumentWithPointer(
            document_index=document.document_index,
            document_length=document.document_length,
            display_length=document.display_length,
            needle_offset=document.needle_offset,
            metadata=document.metadata,
            token_ids=document.token_ids,
            text=document.text,
            shard=document_request.shard,
            pointer=document_request.pointer,
        )

    def get_multiple_documents_by_pointer(
        self,
        document_requests: Iterable[GetDocumentByPointerRequest],
        needle_length: int,
        maximum_context_length: int,
    ) -> List[DocumentWithPointer]:
        documents = self.infini_gram_processor.get_documents_by_pointers_2(
            list_of_shard_and_pointer=[
                (document_request.shard, document_request.pointer)
                for document_request in document_requests
            ],
            needle_length=needle_length,
            maximum_context_length=maximum_context_length,
        )
        mapped_documents = [
            DocumentWithPointer(
                document_index=document.document_index,
                document_length=document.document_length,
                display_length=document.display_length,
                needle_offset=document.needle_offset,
                metadata=document.metadata,
                token_ids=document.token_ids,
                text=document.text,
                shard=document_request.shard,
                pointer=document_request.pointer,
            )
            for (document, document_request) in zip(documents, document_requests)
        ]
        return mapped_documents
