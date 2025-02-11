from math import ceil
from typing import Iterable, List

from opentelemetry import trace

from src.config import get_config
from src.infinigram.processor import (
    BaseInfiniGramResponse,
    Document,
    GetDocumentByIndexRequest,
    InfiniGramProcessor,
    InfiniGramProcessorDependency,
)

tracer = trace.get_tracer(get_config().application_name)


class InfiniGramDocumentResponse(Document, BaseInfiniGramResponse): ...


class InfiniGramDocumentsResponse(BaseInfiniGramResponse):
    documents: Iterable[Document]


class SearchResponse(BaseInfiniGramResponse):
    documents: List[Document]
    page: int
    page_size: int
    page_count: int
    total_documents: int


class DocumentsService:
    infini_gram_processor: InfiniGramProcessor

    def __init__(self, infini_gram_processor: InfiniGramProcessorDependency):
        self.infini_gram_processor = infini_gram_processor

    @tracer.start_as_current_span("documents_service/search_documents")
    def search_documents(
        self,
        search: str,
        maximum_context_length: int,
        page_size: int,
        page: int,
    ) -> SearchResponse:
        search_documents_result = self.infini_gram_processor.search_documents(
            search=search,
            maximum_context_length=maximum_context_length,
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

    @tracer.start_as_current_span("documents_service/get_document_by_index")
    def get_document_by_index(
        self, document_index: int, maximum_context_length: int
    ) -> InfiniGramDocumentResponse:
        document = self.infini_gram_processor.get_document_by_index(
            document_index=document_index,
            maximum_context_length=maximum_context_length,
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

    @tracer.start_as_current_span("documents_service/get_multiple_documents_by_index")
    def get_multiple_documents_by_index(
        self, document_requests: Iterable[GetDocumentByIndexRequest],
    ) -> InfiniGramDocumentsResponse:
        documents = self.infini_gram_processor.get_documents_by_indexes(
            document_requests=document_requests,
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
