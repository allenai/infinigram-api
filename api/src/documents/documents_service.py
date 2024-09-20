import asyncio
from functools import partial
from typing import Iterable

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


class GetDocumentByPointerRequest(BaseModel):
    shard: int
    pointer: int


class DocumentsService:
    infini_gram_processor: InfiniGramProcessor

    def __init__(self, infini_gram_processor: InfiniGramProcessorDependency):
        self.infini_gram_processor = infini_gram_processor

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
            metadata=get_document_by_index_result.metadata,
            token_ids=get_document_by_index_result.token_ids,
        )

    def search_documents(
        self, search: str, maximum_document_display_length: int
    ) -> InfiniGramDocumentsResponse:
        search_documents_result = self.infini_gram_processor.search_documents(
            search=search,
            maximum_document_display_length=maximum_document_display_length,
        )

        mapped_documents = [
            Document(
                text=document.text,
                document_index=document.document_index,
                document_length=document.document_length,
                display_length=document.display_length,
                metadata=document.metadata,
                token_ids=document.token_ids,
            )
            for document in search_documents_result
        ]

        return InfiniGramDocumentsResponse(
            index=self.infini_gram_processor.index, documents=mapped_documents
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
            metadata=document.metadata,
            token_ids=document.token_ids,
            text=document.text,
        )

    async def get_multiple_documents_by_index(
        self, document_indexes: Iterable[int], maximum_document_display_length: int
    ) -> InfiniGramDocumentsResponse:
        async with asyncio.TaskGroup() as tg:
            document_tasks = [
                tg.create_task(
                    asyncio.to_thread(
                        lambda: self.infini_gram_processor.get_document_by_index(
                            document_index=document_index,
                            maximum_document_display_length=maximum_document_display_length,
                        )
                    )
                )
                for document_index in document_indexes
            ]

        documents = [document_task.result() for document_task in document_tasks]
        mapped_documents = [
            Document(
                document_index=document.document_index,
                document_length=document.document_length,
                display_length=document.display_length,
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
            metadata=document.metadata,
            token_ids=document.token_ids,
            text=document.text,
            shard=document_request.shard,
            pointer=document_request.pointer,
        )

    async def get_multiple_documents_by_pointer(
        self,
        document_requests: Iterable[GetDocumentByPointerRequest],
        maximum_document_display_length: int,
    ) -> list[DocumentWithPointer]:
        async with asyncio.TaskGroup() as tg:
            document_tasks = [
                tg.create_task(
                    asyncio.to_thread(
                        partial(self.get_document_by_pointer,
                                document_request=documentRequest,
                                maximum_document_display_length=maximum_document_display_length)
                    )
                )
                for documentRequest in document_requests
            ]

        documents = [document_task.result() for document_task in document_tasks]

        return documents
