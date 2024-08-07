import json
from typing import Annotated, Any, Iterable, List, TypeGuard, TypeVar, cast

from fastapi import Depends
from infini_gram.engine import InfiniGramEngine
from infini_gram.models import (
    AttributionSpan,
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


class InfiniGramCountResponse(BaseInfiniGramResponse):
    approx: bool
    count: int


class Document(CamelCaseModel):
    document_index: int = Field(validation_alias="doc_ix")
    document_length: int = Field(validation_alias="doc_len")
    display_length: int = Field(validation_alias="disp_len")
    metadata: dict[str, Any]
    token_ids: List[int]
    text: str


class DocumentWithPointer(Document):
    shard: int
    pointer: int


class InfiniGramAttributionResponse(BaseInfiniGramResponse):
    spans: List[AttributionSpan]
    input_token_ids: List[int]


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
        return self.tokenizer.decode(token_ids)  # type: ignore [no-any-return]

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
    ) -> Document:
        get_doc_by_rank_response = self.infini_gram_engine.get_doc_by_rank(
            s=shard, rank=rank, max_disp_len=maximum_document_display_length
        )

        doc_result = self.__handle_error(get_doc_by_rank_response)

        parsed_metadata = json.loads(doc_result["metadata"])
        decoded_text = self.decode_tokens(doc_result["token_ids"])

        return Document(
            document_index=doc_result["doc_ix"],
            document_length=doc_result["doc_len"],
            display_length=doc_result["disp_len"],
            metadata=parsed_metadata,
            token_ids=doc_result["token_ids"],
            text=decoded_text,
        )

    def get_document_by_index(
        self, document_index: int, maximum_document_display_length: int
    ) -> Document:
        get_doc_by_index_response = self.infini_gram_engine.get_doc_by_ix(
            doc_ix=document_index, max_disp_len=maximum_document_display_length
        )

        doc_result = self.__handle_error(get_doc_by_index_response)

        parsed_metadata = json.loads(doc_result["metadata"])
        decoded_text = self.decode_tokens(doc_result["token_ids"])

        return Document(
            document_index=doc_result["doc_ix"],
            document_length=doc_result["doc_len"],
            display_length=doc_result["disp_len"],
            metadata=parsed_metadata,
            token_ids=doc_result["token_ids"],
            text=decoded_text,
        )

    def search_documents(
        self, search: str, maximum_document_display_length: int
    ) -> List[Document]:
        tokenized_query_ids = self.tokenize(search)
        matching_documents = self.infini_gram_engine.find(input_ids=tokenized_query_ids)

        matching_documents_result = self.__handle_error(matching_documents)

        docs: List[Document] = []
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

        return docs

    # Attribute doesn't return a high-level response, it just returns stuff from the engine. Use this inside a service instead of returning it directly
    def attribute(
        self,
        input: str,
        delimiters: List[str],
        minimum_span_length: int,
        maximum_frequency: int,
    ) -> InfiniGramAttributionResponse:
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

        return InfiniGramAttributionResponse(
            **attribute_result, index=self.index, input_token_ids=input_ids
        )

    def get_document_by_pointer(
        self, shard: int, pointer: int, maximum_document_display_length: int
    ) -> Document:
        document_response = self.infini_gram_engine.get_doc_by_ptr(
            s=shard, ptr=pointer, max_disp_len=maximum_document_display_length
        )

        document_result = self.__handle_error(result=document_response)

        parsed_metadata = json.loads(document_result["metadata"])
        decoded_text = self.decode_tokens(document_result["token_ids"])

        return Document(
            document_index=document_result["doc_ix"],
            document_length=document_result["doc_len"],
            display_length=document_result["disp_len"],
            metadata=parsed_metadata,
            token_ids=document_result["token_ids"],
            text=decoded_text,
        )
        return document_result


indexes = {index: InfiniGramProcessor(index) for index in AvailableInfiniGramIndexId}


def InfiniGramProcessorFactoryPathParam(
    index: AvailableInfiniGramIndexId,
) -> InfiniGramProcessor:
    return indexes[index]


InfiniGramProcessorDependency = Annotated[
    InfiniGramProcessor, Depends(InfiniGramProcessorFactoryPathParam)
]
