import json
from typing import Annotated, Any, Iterable, List, Sequence, TypeGuard, TypeVar, cast

from fastapi import Depends
from infini_gram.engine import InfiniGramEngine
from infini_gram.models import (
    AttributionResponse,
    DocResult,
    ErrorResponse,
    InfiniGramEngineResponse,
)
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
    text: str
    tokens: Sequence[int]


class AttributionSpanWithDocuments(AttributionSpan):
    documents: Sequence[FullAttributionDocument]


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

    def tokenize(
        self, input: TextInput | PreTokenizedInput | EncodedInput
    ) -> List[int]:
        encoded_query: List[int] = self.tokenizer.encode(input)
        return encoded_query

    def decode_tokens(self, token_ids: Iterable[int]) -> str:
        return self.tokenizer.decode(token_ids)

    def __handle_error(
        self,
        result: InfiniGramEngineResponse[TInfiniGramResponse],
    ) -> TInfiniGramResponse:
        if is_infini_gram_error_response(result):
            raise InfiniGramEngineException(detail=result["error"])

        return cast(TInfiniGramResponse, result)

    def count_n_gram(self, query: str) -> InfiniGramCountResponse:
        tokenized_query_ids = self.tokenize(query)

        count_response = self.infini_gram_engine.count(input_ids=tokenized_query_ids)

        count_result = self.__handle_error(count_response)

        return InfiniGramCountResponse(index=self.index, **count_result)

    def get_document_by_rank(
        self, shard: int, rank: int, maximum_document_display_length: int
    ) -> InfiniGramRankResponse:
        get_doc_by_rank_response = self.infini_gram_engine.get_doc_by_rank(
            s=shard, rank=rank, max_disp_len=maximum_document_display_length
        )

        doc_result = self.__handle_error(get_doc_by_rank_response)

        parsed_metadata = json.loads(doc_result["metadata"])
        decoded_text = self.decode_tokens(doc_result["token_ids"])

        return InfiniGramRankResponse(
            index=self.index,
            text=decoded_text,
            document_index=doc_result["doc_ix"],
            document_length=doc_result["doc_len"],
            display_length=doc_result["disp_len"],
            metadata=parsed_metadata,
            token_ids=doc_result["token_ids"],
        )

    def search_documents(
        self, search: str, maximum_document_display_length: int
    ) -> InfiniGramDocumentsResponse:
        tokenized_query_ids = self.tokenize(search)
        matching_documents = self.infini_gram_engine.find(input_ids=tokenized_query_ids)

        matching_documents_result = self.__handle_error(matching_documents)

        docs = []
        for shard, (start, end) in enumerate(
            matching_documents_result["segment_by_shard"]
        ):
            for rank in range(start, end):
                doc = self.get_document_by_rank(
                    shard=shard,
                    rank=rank,
                    maximum_document_display_length=maximum_document_display_length,
                )
                docs.append(doc)

        return InfiniGramDocumentsResponse(index=self.index, documents=docs)

    # Attribute doesn't return a high-level response, it just returns stuff from the engine. Use this inside a service instead of returning it directly
    def attribute(
        self,
        input: str,
        delimiters: List[str],
        minimum_span_length: int,
        maximum_frequency: int,
    ) -> AttributionResponse:
        input_ids = self.tokenize(input)

        delimiter_token_ids: Iterable[int] = (
            self.tokenize(delimiters) if len(delimiters) > 0 else []
        )

        attribute_response = self.infini_gram_engine.attribute(
            input_ids=input_ids,
            delim_ids=delimiter_token_ids,
            min_len=minimum_span_length,
            max_cnt=maximum_frequency,
        )

        attribute_result = self.__handle_error(attribute_response)

        return attribute_result

    # get_document_by_pointer doesn't return a high-level response, it just returns stuff from the engine. Use this inside a service instead of returning it directly
    def get_document_by_pointer(
        self, shard: int, pointer: int, maximum_document_display_length: int
    ) -> DocResult:
        document_response = self.infini_gram_engine.get_doc_by_ptr(
            s=shard, ptr=pointer, max_disp_len=maximum_document_display_length
        )

        document_result = self.__handle_error(result=document_response)

        return document_result


indexes = {index: InfiniGramProcessor(index) for index in AvailableInfiniGramIndexId}


def InfiniGramProcessorFactoryPathParam(
    index: AvailableInfiniGramIndexId,
) -> InfiniGramProcessor:
    return indexes[index]


InfiniGramProcessorDependency = Annotated[
    InfiniGramProcessor, Depends(InfiniGramProcessorFactoryPathParam)
]
