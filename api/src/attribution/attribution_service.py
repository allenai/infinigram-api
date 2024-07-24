import json
from itertools import islice
from typing import List, Sequence

from src.camel_case_model import CamelCaseModel
from src.infinigram.processor import (
    BaseInfiniGramResponse,
    Document,
    InfiniGramProcessor,
    InfiniGramProcessorDependency,
)


class AttributionDocument(CamelCaseModel):
    shard: int
    pointer: int
    document_index: int


class FullAttributionDocument(AttributionDocument, Document):
    text: str


class AttributionSpan(CamelCaseModel):
    left: int
    right: int
    length: int
    documents: Sequence[AttributionDocument]
    text: str
    tokenIds: Sequence[int]


class AttributionSpanWithDocuments(AttributionSpan):
    documents: Sequence[FullAttributionDocument]


class InfiniGramAttributionResponse(BaseInfiniGramResponse):
    spans: Sequence[AttributionSpan]


class InfiniGramAttributionResponseWithDocs(InfiniGramAttributionResponse):
    spans: Sequence[AttributionSpanWithDocuments]


class AttributionService:
    infini_gram_processor: InfiniGramProcessor

    def __init__(self, infini_gram_processor: InfiniGramProcessorDependency):
        self.infini_gram_processor = infini_gram_processor

    def get_attribution_for_response(
        self,
        prompt_response: str,
        delimiters: List[str],
        minimum_span_length: int,
        maximum_frequency: int,
        include_documents: bool,
        maximum_document_display_length: int,
    ) -> InfiniGramAttributionResponse:
        attribute_result = self.infini_gram_processor.attribute(
            input=prompt_response,
            delimiters=delimiters,
            minimum_span_length=minimum_span_length,
            maximum_frequency=maximum_frequency,
        )

        if include_documents:
            spans_with_documents: List[AttributionSpanWithDocuments] = []
            for span in attribute_result.spans:
                documents: List[FullAttributionDocument] = []
                for document in span["docs"]:
                    document_result = self.infini_gram_processor.get_document_by_pointer(
                        shard=document["s"],
                        pointer=document["ptr"],
                        maximum_document_display_length=maximum_document_display_length,
                    )

                    new_document = FullAttributionDocument(
                        document_index=document["doc_ix"],
                        document_length=document_result["doc_len"],
                        display_length=document_result["disp_len"],
                        metadata=json.loads(document_result["metadata"]),
                        token_ids=document_result["token_ids"],
                        shard=document["s"],
                        pointer=document["ptr"],
                        text=self.infini_gram_processor.decode_tokens(
                            document_result["token_ids"]
                        ),
                    )
                    documents.append(new_document)

                span_text_tokens = list(
                    islice(attribute_result.input_token_ids, span["l"], span["r"])
                )
                span_text = self.infini_gram_processor.decode_tokens(
                    token_ids=span_text_tokens
                )
                new_span = AttributionSpanWithDocuments(
                    left=span["l"],
                    right=span["r"],
                    length=span["length"],
                    documents=documents,
                    text=span_text,
                    tokenIds=span_text_tokens,
                )

                spans_with_documents.append(new_span)

            return InfiniGramAttributionResponseWithDocs(
                index=self.infini_gram_processor.index, spans=spans_with_documents
            )

        else:
            spans: List[AttributionSpan] = []
            for span in attribute_result.spans:
                span_text_tokens = list(
                    islice(attribute_result.input_token_ids, span["l"], span["r"])
                )
                span_text = self.infini_gram_processor.decode_tokens(
                    token_ids=span_text_tokens
                )

                spans.append(
                    AttributionSpan(
                        left=span["l"],
                        right=span["r"],
                        length=span["length"],
                        text=span_text,
                        tokenIds=span_text_tokens,
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
                index=self.infini_gram_processor.index, spans=spans
            )
