from itertools import islice
from typing import Generic, Iterable, List, Optional, Sequence, TypeVar

import numpy as np
from pydantic import Field
from rank_bm25 import BM25Okapi  # type: ignore

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
        maximum_span_density: float,
        minimum_span_length: int,
        maximum_frequency: int,
        maximum_document_display_length: int,
        include_documents: bool = False,
        include_input_as_tokens: bool = False,
        allow_spans_with_partial_words: bool = False,
        filter_method: str = 'none',
        filter_bm25_ratio_to_keep: float = 1.0,
    ) -> InfiniGramAttributionResponse | InfiniGramAttributionResponseWithDocuments:
        attribute_result = self.infini_gram_processor.attribute(
            input=prompt_response,
            delimiters=delimiters,
            maximum_span_density=maximum_span_density,
            minimum_span_length=minimum_span_length,
            maximum_frequency=maximum_frequency,
            allow_spans_with_partial_words=allow_spans_with_partial_words,
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

                documents = self.documents_service.get_multiple_documents_by_pointer(
                        document_requests=document_requests,
                        maximum_document_display_length=maximum_document_display_length,
                    )

                (span_text_tokens, span_text) = self.__get_span_text(
                    input_token_ids=attribute_result.input_token_ids,
                    start=span["l"],
                    stop=span["r"],
                )

                span_with_document = AttributionSpanWithDocuments(
                    left=span["l"],
                    right=span["r"],
                    length=span["length"],
                    documents=documents,
                    text=span_text,
                    token_ids=span_text_tokens,
                )

                spans_with_documents.append(span_with_document)

            # Filter documents using BM25
            if filter_method == 'bm25':
                docs = [doc.text for span_with_document in spans_with_documents for doc in span_with_document.documents]
                tokenized_corpus = [doc.split(" ") for doc in docs]
                bm25 = BM25Okapi(tokenized_corpus)
                doc_scores = bm25.get_scores(prompt_response.split(" "))

                # keep the top ratio_to_keep documents
                ratio_to_keep = filter_bm25_ratio_to_keep
                num_docs_to_keep = int(np.ceil(len(docs) * ratio_to_keep))
                indices_to_keep = np.argsort(doc_scores)[-num_docs_to_keep:]

                new_spans_with_documents = []
                i = 0
                for span_with_document in spans_with_documents:
                    new_documents = []
                    for j in range(len(span_with_document.documents)):
                        if i in indices_to_keep:
                            span_with_document.documents[j].relevance_score = doc_scores[i]
                            new_documents.append(span_with_document.documents[j])
                        i += 1
                    if len(new_documents) > 0:
                        new_spans_with_documents.append(
                            AttributionSpanWithDocuments(
                                left=span_with_document.left,
                                right=span_with_document.right,
                                length=span_with_document.length,
                                documents=new_documents,
                                text=span_with_document.text,
                                token_ids=span_with_document.token_ids,
                            )
                        )
                spans_with_documents = new_spans_with_documents

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
