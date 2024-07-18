import json
from typing import Annotated, Any, Iterable, List, Sequence, TypeGuard, TypeVar, cast

from fastapi import Depends
from infini_gram.engine import InfiniGramEngine
from infini_gram.models import ErrorResponse, InfiniGramEngineResponse
from pydantic import Field
from transformers import AutoTokenizer, PreTrainedTokenizerBase  # type: ignore
from transformers.tokenization_utils_base import (  # type: ignore
    EncodedInput,
    PreTokenizedInput,
    TextInput,
)

from src.camel_case_model import CamelCaseModel
from src.infinigram.index_mappings import AvailableInfiniGramIndexId, index_mappings
from src.infinigram.infini_gram_engine_exception import InfiniGramEngineException


class BaseInfiniGramResponse(CamelCaseModel):
    index: str


class InfiniGramErrorResponse(CamelCaseModel):
    error: str


class Document(CamelCaseModel):
    document_index: int = Field(validation_alias="doc_ix")
    document_length: int = Field(validation_alias="doc_len")
    display_length: int = Field(validation_alias="disp_len")
    metadata: dict[str, Any]
    token_ids: List[int]


class InfiniGramQueryResponse(BaseInfiniGramResponse):
    approx: bool
    count: int = Field(validation_alias="cnt")
    documents: Iterable[Document]
    indexes: Iterable[int] = Field(validation_alias="idxs")


class InfiniGramCountResponse(BaseInfiniGramResponse):
    approx: bool
    count: int


class InfiniGramRankResponse(Document, BaseInfiniGramResponse):
    text: str


class InfiniGramDocumentsResponse(BaseInfiniGramResponse):
    documents: Iterable[InfiniGramRankResponse]


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


class AttributionSpanWithDocuments(AttributionSpan):
    documents: Sequence[FullAttributionDocument]


class InfiniGramAttributionResponse(BaseInfiniGramResponse):
    spans: Sequence[AttributionSpan]


class InfiniGramAttributionResponseWithDocs(InfiniGramAttributionResponse):
    spans: Sequence[AttributionSpanWithDocuments]


TInfiniGramResponse = TypeVar("TInfiniGramResponse")


def is_infini_gram_error_response(
    val: InfiniGramEngineResponse[TInfiniGramResponse],
) -> TypeGuard[ErrorResponse]:
    return isinstance(val, dict) and "error" in val


class InfiniGramProcessor:
    index: str
    tokenizer: PreTrainedTokenizerBase
    infini_gram_engine: InfiniGramEngine

    def __init__(self, index: AvailableInfiniGramIndexId):
        self.index = index.value
        index_mapping = index_mappings[index.value]

        self.tokenizer = AutoTokenizer.from_pretrained(
            index_mapping["tokenizer"],
            add_bos_token=False,
            add_eos_token=False,
            trust_remote_code=True,
        )

        if self.tokenizer.eos_token_id is None:
            raise Exception("An indexer didn't have an eos token id")

        self.infini_gram_engine = InfiniGramEngine(
            index_dir=index_mapping["index_dir"],
            eos_token_id=self.tokenizer.eos_token_id,
        )

    def __tokenize(
        self, query: TextInput | PreTokenizedInput | EncodedInput
    ) -> Iterable[int]:
        encoded_query: Iterable[int] = self.tokenizer.encode(query)
        return encoded_query

    def __handle_error(
        self,
        result: InfiniGramEngineResponse[TInfiniGramResponse],
    ) -> TInfiniGramResponse:
        if is_infini_gram_error_response(result):
            raise InfiniGramEngineException(detail=result["error"])

        return cast(TInfiniGramResponse, result)

    def find_docs_with_query(self, query: str) -> InfiniGramQueryResponse:
        tokenized_query_ids = self.__tokenize(query)

        docs_result = self.infini_gram_engine.search_docs(
            input_ids=tokenized_query_ids, maxnum=1, max_disp_len=10
        )

        result = self.__handle_error(docs_result)

        mapped_documents = [
            Document(
                document_index=doc_result["doc_ix"],
                document_length=doc_result["doc_len"],
                display_length=doc_result["disp_len"],
                metadata=json.loads(doc_result["metadata"]),
                token_ids=doc_result["token_ids"],
            )
            for doc_result in result["documents"]
        ]

        return InfiniGramQueryResponse(
            index=self.index,
            count=result["cnt"],
            documents=mapped_documents,
            approx=result["approx"],
            indexes=result["idxs"],
        )

    def count_n_gram(self, query: str) -> InfiniGramCountResponse:
        tokenized_query_ids = self.__tokenize(query)

        count_response = self.infini_gram_engine.count(input_ids=tokenized_query_ids)

        count_result = self.__handle_error(count_response)

        return InfiniGramCountResponse(index=self.index, **count_result)

    def rank(self, shard: int, rank: int) -> InfiniGramRankResponse:
        get_doc_by_rank_response = self.infini_gram_engine.get_doc_by_rank(
            s=shard, rank=rank, max_disp_len=10
        )

        doc_result = self.__handle_error(get_doc_by_rank_response)

        parsed_metadata = json.loads(doc_result["metadata"])
        decoded_text = self.tokenizer.decode(doc_result["token_ids"])

        return InfiniGramRankResponse(
            index=self.index,
            text=decoded_text,
            document_index=doc_result["doc_ix"],
            document_length=doc_result["doc_len"],
            display_length=doc_result["disp_len"],
            metadata=parsed_metadata,
            token_ids=doc_result["token_ids"],
        )

    def get_documents(self, search: str) -> InfiniGramDocumentsResponse:
        tokenized_query_ids = self.__tokenize(search)
        matching_documents = self.infini_gram_engine.find(input_ids=tokenized_query_ids)

        matching_documents_result = self.__handle_error(matching_documents)

        docs = []
        for shard, (start, end) in enumerate(
            matching_documents_result["segment_by_shard"]
        ):
            for rank in range(start, end):
                doc = self.rank(shard=shard, rank=rank)
                docs.append(doc)

        return InfiniGramDocumentsResponse(index=self.index, documents=docs)

    def get_attribution_for_response(
        self,
        search: str,
        delimiters: List[str],
        minimum_span_length: int,
        maximum_frequency: int,
        include_documents: bool,
        maximum_document_display_length: int,
    ) -> InfiniGramAttributionResponse:
        tokenized_query_ids = self.__tokenize(query=search)

        tokenized_delimiters: Iterable[int] = (
            self.__tokenize(query=delimiters) if len(delimiters) > 0 else []
        )

        attribute_response = self.infini_gram_engine.attribute(
            input_ids=tokenized_query_ids,
            delim_ids=tokenized_delimiters,
            min_len=minimum_span_length,
            max_cnt=maximum_frequency,
        )

        attribute_result = self.__handle_error(attribute_response)

        if include_documents:
            spans_with_documents: List[AttributionSpanWithDocuments] = []
            for span in attribute_result["spans"]:
                documents: List[FullAttributionDocument] = []
                for document in span["docs"]:
                    infini_gram_document = self.infini_gram_engine.get_doc_by_ptr(
                        s=document["s"],
                        ptr=document["ptr"],
                        max_disp_len=maximum_document_display_length,
                    )

                    document_result = self.__handle_error(infini_gram_document)

                    new_document = FullAttributionDocument(
                        document_index=document["doc_ix"],
                        document_length=document_result["doc_len"],
                        display_length=document_result["disp_len"],
                        metadata=json.loads(document_result["metadata"]),
                        token_ids=document_result["token_ids"],
                        shard=document["s"],
                        pointer=document["ptr"],
                        text=self.tokenizer.decode(document_result["token_ids"]),
                    )
                    documents.append(new_document)

                new_span = AttributionSpanWithDocuments(
                    left=span["l"],
                    right=span["r"],
                    length=span["length"],
                    documents=documents,
                )

                spans_with_documents.append(new_span)

            return InfiniGramAttributionResponseWithDocs(
                index=self.index, spans=spans_with_documents
            )

        else:
            spans = [
                AttributionSpan(
                    left=span["l"],
                    right=span["r"],
                    length=span["length"],
                    documents=[
                        AttributionDocument(
                            shard=document["s"],
                            pointer=document["ptr"],
                            document_index=document["doc_ix"],
                        )
                        for document in span["docs"]
                    ],
                )
                for span in attribute_result["spans"]
            ]

            return InfiniGramAttributionResponse(index=self.index, spans=spans)


indexes = {index: InfiniGramProcessor(index) for index in AvailableInfiniGramIndexId}


def InfiniGramProcessorFactoryPathParam(
    index: AvailableInfiniGramIndexId,
) -> InfiniGramProcessor:
    return indexes[index]


InfiniGramProcessorDependency = Annotated[
    InfiniGramProcessor, Depends(InfiniGramProcessorFactoryPathParam)
]
