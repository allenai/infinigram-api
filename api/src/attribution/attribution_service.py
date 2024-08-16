from itertools import islice
from typing import Generic, Iterable, List, Optional, Sequence, TypeVar

from pydantic import Field

from src.camel_case_model import CamelCaseModel
from src.documents.documents_router import DocumentsServiceDependency
from src.documents.documents_service import (
    DocumentsService,
    GetDocumentByPointerRequest,
)
from src.infinigram.processor import (
    BaseInfiniGramResponse,
    DocumentWithPointer,
    InfiniGramProcessor,
    InfiniGramProcessorDependency,
)


class AttributionDocument(CamelCaseModel):
    shard: int
    pointer: int
    document_index: int


TAttributionDocument = TypeVar("TAttributionDocument")


class BaseAttributionSpan(CamelCaseModel, Generic[TAttributionDocument]):
    left: int
    right: int
    length: int
    text: str
    token_ids: Sequence[int]
    documents: Sequence[TAttributionDocument]


class AttributionSpan(BaseAttributionSpan[AttributionDocument]): ...


class AttributionSpanWithDocuments(BaseAttributionSpan[DocumentWithPointer]): ...


TAttributionSpan = TypeVar("TAttributionSpan")


class BaseInfinigramAttributionResponse(
    BaseInfiniGramResponse, Generic[TAttributionSpan]
):
    spans: Sequence[TAttributionSpan]
    input_tokens: Optional[Sequence[str]] = Field(
        examples=[["busy", " medieval", " streets", "."]]
    )


class InfiniGramAttributionResponse(
    BaseInfinigramAttributionResponse[AttributionSpan]
): ...


class InfiniGramAttributionResponseWithDocuments(
    BaseInfinigramAttributionResponse[AttributionSpanWithDocuments]
): ...


class AttributionService:
    infini_gram_processor: InfiniGramProcessor
    documents_service: DocumentsService

    def __init__(
        self,
        infini_gram_processor: InfiniGramProcessorDependency,
        documents_service: DocumentsServiceDependency,
    ):
        self.infini_gram_processor = infini_gram_processor
        self.documents_service = documents_service

    def __get_span_text(
        self, input_token_ids: Iterable[int], start: int, stop: int
    ) -> tuple[Sequence[int], str]:
        span_text_tokens = list(islice(input_token_ids, start, stop))
        span_text = self.infini_gram_processor.decode_tokens(token_ids=span_text_tokens)

        return (span_text_tokens, span_text)

    async def get_attribution_for_response(
        self,
        prompt_response: str,
        delimiters: List[str],
        minimum_span_length: int,
        maximum_frequency: int,
        maximum_document_display_length: int,
        include_documents: Optional[bool] = False,
        include_input_as_tokens: Optional[bool] = False,
    ) -> InfiniGramAttributionResponse | InfiniGramAttributionResponseWithDocuments:
        attribute_result = self.infini_gram_processor.attribute(
            input=prompt_response,
            delimiters=delimiters,
            minimum_span_length=minimum_span_length,
            maximum_frequency=maximum_frequency,
        )

        if include_documents:
            spans_with_documents: List[AttributionSpanWithDocuments] = []

            for span in attribute_result.spans:
                document_requests: List[GetDocumentByPointerRequest] = [
                    GetDocumentByPointerRequest(
                        shard=document["s"], pointer=document["ptr"]
                    )
                    for document in span["docs"]
                ]

                documents = (
                    await self.documents_service.get_multiple_documents_by_pointer(
                        document_requests=document_requests,
                        maximum_document_display_length=maximum_document_display_length,
                    )
                )

                (span_text_tokens, span_text) = self.__get_span_text(
                    input_token_ids=attribute_result.input_token_ids,
                    start=span["l"],
                    stop=span["r"],
                )

                new_span = AttributionSpanWithDocuments(
                    left=span["l"],
                    right=span["r"],
                    length=span["length"],
                    documents=documents,
                    text=span_text,
                    token_ids=span_text_tokens,
                )

                spans_with_documents.append(new_span)

            return InfiniGramAttributionResponseWithDocuments(
                index=self.infini_gram_processor.index,
                spans=spans_with_documents,
                input_tokens=self.infini_gram_processor.tokenize_to_list(
                    prompt_response
                )
                if include_input_as_tokens
                else None,
            )

        else:
            spans: List[AttributionSpan] = []
            for span in attribute_result.spans:
                (span_text_tokens, span_text) = self.__get_span_text(
                    input_token_ids=attribute_result.input_token_ids,
                    start=span["l"],
                    stop=span["r"],
                )

                spans.append(
                    AttributionSpan(
                        left=span["l"],
                        right=span["r"],
                        length=span["length"],
                        text=span_text,
                        token_ids=span_text_tokens,
                        documents=[
                            AttributionDocument(
                                shard=document["s"],
                                pointer=document["ptr"],
                                document_index=document["doc_ix"],
                            )
                            for document in span["docs"]
                        ],
                    )
                )

            return InfiniGramAttributionResponse(
                index=self.infini_gram_processor.index,
                spans=spans,
                input_tokens=self.infini_gram_processor.tokenize_to_list(
                    prompt_response
                )
                if include_input_as_tokens
                else None,
            )
