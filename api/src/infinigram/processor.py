from enum import Enum
import json
from typing import (
    Annotated,
    Any,
    Iterable,
    List,
    Sequence,
    Tuple,
    TypeGuard,
    TypeVar,
    cast,
)

import numpy as np
from fastapi import Depends
from infini_gram.engine import InfiniGramEngine
from infini_gram.models import (
    AttributionSpan,
    ErrorResponse,
    InfiniGramEngineResponse,
)
from pydantic import Field
from transformers.tokenization_utils_base import (  # type: ignore
    EncodedInput,
    PreTokenizedInput,
    TextInput,
)

from src.camel_case_model import CamelCaseModel
from src.infinigram.index_mappings import AvailableInfiniGramIndexId, index_mappings
from src.infinigram.infini_gram_engine_exception import InfiniGramEngineException

from .tokenizers.tokenizer import Tokenizer


class SpanRankingMethod(Enum):
    LENGTH = "length"
    UNIGRAM_LOGPROB_SUM = "unigram_logprob_sum"


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
    needle_offset: int = Field(validation_alias="needle_offset")
    metadata: dict[str, Any]
    token_ids: List[int]
    text: str
    relevance_score: float | None = None


class DocumentWithPointer(Document):
    shard: int
    pointer: int


class InfiniGramAttributionResponse(BaseInfiniGramResponse):
    spans: List[AttributionSpan]
    input_token_ids: List[int]


class InfiniGramSearchResponse(CamelCaseModel):
    documents: List[Document]
    total_documents: int


TInfiniGramResponse = TypeVar("TInfiniGramResponse")


def is_infini_gram_error_response(
    val: InfiniGramEngineResponse[TInfiniGramResponse],
) -> TypeGuard[ErrorResponse]:
    return isinstance(val, dict) and "error" in val


class InfiniGramProcessor:
    index: str
    tokenizer: Tokenizer
    infini_gram_engine: InfiniGramEngine

    def __init__(self, index: AvailableInfiniGramIndexId):
        self.index = index.value
        index_mapping = index_mappings[index.value]

        self.tokenizer = index_mapping["tokenizer"]

        self.infini_gram_engine = InfiniGramEngine(
            index_dir=index_mapping["index_dir"],
            eos_token_id=self.tokenizer.eos_token_id,
            bow_ids_path=self.tokenizer.bow_ids_path,
            precompute_unigram_logprobs=True,
            # for the attribution feature, disabling prefetching on ds and sa can speed things up
            ds_prefetch_depth=0,
            sa_prefetch_depth=0,
            od_prefetch_depth=3,
        )

    def tokenize(
        self, input: TextInput | PreTokenizedInput | EncodedInput
    ) -> List[int]:
        return self.tokenizer.tokenize(input)

    def decode_tokens(self, token_ids: Iterable[int]) -> str:
        return self.tokenizer.decode_tokens(token_ids)

    def tokenize_to_list(self, input: TextInput) -> Sequence[str]:
        return self.tokenizer.tokenize_to_list(input)

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
            needle_offset=doc_result["needle_offset"],
            metadata=parsed_metadata,
            token_ids=doc_result["token_ids"],
            text=decoded_text,
        )

    def get_documents_by_ranks(
        self,
        list_of_shard_and_rank: List[Tuple[int, int]],
        maximum_document_display_length: int,
    ) -> List[Document]:
        get_docs_by_ranks_response = self.infini_gram_engine.get_docs_by_ranks(
            list_of_s_and_rank=list_of_shard_and_rank,
            max_disp_len=maximum_document_display_length,
        )

        doc_results = self.__handle_error(get_docs_by_ranks_response)

        documents = []
        for doc_result in doc_results:
            parsed_metadata = json.loads(doc_result["metadata"])
            decoded_text = self.decode_tokens(doc_result["token_ids"])

            documents.append(
                Document(
                    document_index=doc_result["doc_ix"],
                    document_length=doc_result["doc_len"],
                    display_length=doc_result["disp_len"],
                    needle_offset=doc_result["needle_offset"],
                    metadata=parsed_metadata,
                    token_ids=doc_result["token_ids"],
                    text=decoded_text,
                )
            )

        return documents

    def get_document_by_pointer(
        self, shard: int, pointer: int, maximum_document_display_length: int
    ) -> Document:
        document_response = self.infini_gram_engine.get_doc_by_ptr(
            s=shard, ptr=pointer, max_disp_len=maximum_document_display_length
        )

        doc_result = self.__handle_error(result=document_response)

        parsed_metadata = json.loads(doc_result["metadata"])
        decoded_text = self.decode_tokens(doc_result["token_ids"])

        return Document(
            document_index=doc_result["doc_ix"],
            document_length=doc_result["doc_len"],
            display_length=doc_result["disp_len"],
            needle_offset=doc_result["needle_offset"],
            metadata=parsed_metadata,
            token_ids=doc_result["token_ids"],
            text=decoded_text,
        )

    def get_documents_by_pointers(
        self,
        list_of_shard_and_pointer: List[Tuple[int, int]],
        maximum_document_display_length: int,
    ) -> List[Document]:
        get_docs_by_pointers_response = self.infini_gram_engine.get_docs_by_ptrs(
            list_of_s_and_ptr=list_of_shard_and_pointer,
            max_disp_len=maximum_document_display_length,
        )

        doc_results = self.__handle_error(get_docs_by_pointers_response)

        documents = []
        for doc_result in doc_results:
            parsed_metadata = json.loads(doc_result["metadata"])
            decoded_text = self.decode_tokens(doc_result["token_ids"])

            documents.append(
                Document(
                    document_index=doc_result["doc_ix"],
                    document_length=doc_result["doc_len"],
                    display_length=doc_result["disp_len"],
                    needle_offset=doc_result["needle_offset"],
                    metadata=parsed_metadata,
                    token_ids=doc_result["token_ids"],
                    text=decoded_text,
                )
            )

        return documents

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
            needle_offset=doc_result["needle_offset"],
            metadata=parsed_metadata,
            token_ids=doc_result["token_ids"],
            text=decoded_text,
        )

    def get_documents_by_indexes(
        self, list_of_document_index: List[int], maximum_document_display_length: int
    ) -> List[Document]:
        get_docs_by_indexes_response = self.infini_gram_engine.get_docs_by_ixs(
            list_of_doc_ix=list_of_document_index,
            max_disp_len=maximum_document_display_length,
        )

        doc_results = self.__handle_error(get_docs_by_indexes_response)

        documents = []
        for doc_result in doc_results:
            parsed_metadata = json.loads(doc_result["metadata"])
            decoded_text = self.decode_tokens(doc_result["token_ids"])

            documents.append(
                Document(
                    document_index=doc_result["doc_ix"],
                    document_length=doc_result["doc_len"],
                    display_length=doc_result["disp_len"],
                    needle_offset=doc_result["needle_offset"],
                    metadata=parsed_metadata,
                    token_ids=doc_result["token_ids"],
                    text=decoded_text,
                )
            )

        return documents

    def get_document_by_rank_2(
        self, shard: int, rank: int, needle_length: int, maximum_context_length: int
    ) -> Document:
        get_doc_by_rank_response = self.infini_gram_engine.get_doc_by_rank_2(
            s=shard,
            rank=rank,
            needle_len=needle_length,
            max_ctx_len=maximum_context_length,
        )

        doc_result = self.__handle_error(get_doc_by_rank_response)

        parsed_metadata = json.loads(doc_result["metadata"])
        decoded_text = self.decode_tokens(doc_result["token_ids"])

        return Document(
            document_index=doc_result["doc_ix"],
            document_length=doc_result["doc_len"],
            display_length=doc_result["disp_len"],
            needle_offset=doc_result["needle_offset"],
            metadata=parsed_metadata,
            token_ids=doc_result["token_ids"],
            text=decoded_text,
        )

    def get_documents_by_ranks_2(
        self,
        list_of_shard_and_rank: List[Tuple[int, int]],
        needle_length: int,
        maximum_context_length: int,
    ) -> List[Document]:
        get_docs_by_ranks_response = self.infini_gram_engine.get_docs_by_ranks_2(
            list_of_s_and_rank=list_of_shard_and_rank,
            needle_len=needle_length,
            max_ctx_len=maximum_context_length,
        )

        doc_results = self.__handle_error(get_docs_by_ranks_response)

        documents = []
        for doc_result in doc_results:
            parsed_metadata = json.loads(doc_result["metadata"])
            decoded_text = self.decode_tokens(doc_result["token_ids"])

            documents.append(
                Document(
                    document_index=doc_result["doc_ix"],
                    document_length=doc_result["doc_len"],
                    display_length=doc_result["disp_len"],
                    needle_offset=doc_result["needle_offset"],
                    metadata=parsed_metadata,
                    token_ids=doc_result["token_ids"],
                    text=decoded_text,
                )
            )

        return documents

    def get_document_by_pointer_2(
        self, shard: int, pointer: int, needle_length: int, maximum_context_length: int
    ) -> Document:
        document_response = self.infini_gram_engine.get_doc_by_ptr_2(
            s=shard,
            ptr=pointer,
            needle_len=needle_length,
            max_ctx_len=maximum_context_length,
        )

        document_result = self.__handle_error(result=document_response)

        parsed_metadata = json.loads(document_result["metadata"])
        decoded_text = self.decode_tokens(document_result["token_ids"])

        return Document(
            document_index=document_result["doc_ix"],
            document_length=document_result["doc_len"],
            display_length=document_result["disp_len"],
            needle_offset=document_result["needle_offset"],
            metadata=parsed_metadata,
            token_ids=document_result["token_ids"],
            text=decoded_text,
        )

    def get_documents_by_pointers_2(
        self,
        list_of_shard_and_pointer: List[Tuple[int, int]],
        needle_length: int,
        maximum_context_length: int,
    ) -> List[Document]:
        get_docs_by_pointers_response = self.infini_gram_engine.get_docs_by_ptrs_2(
            list_of_s_and_ptr=list_of_shard_and_pointer,
            needle_len=needle_length,
            max_ctx_len=maximum_context_length,
        )

        doc_results = self.__handle_error(get_docs_by_pointers_response)

        documents = []
        for doc_result in doc_results:
            parsed_metadata = json.loads(doc_result["metadata"])
            decoded_text = self.decode_tokens(doc_result["token_ids"])

            documents.append(
                Document(
                    document_index=doc_result["doc_ix"],
                    document_length=doc_result["doc_len"],
                    display_length=doc_result["disp_len"],
                    needle_offset=doc_result["needle_offset"],
                    metadata=parsed_metadata,
                    token_ids=doc_result["token_ids"],
                    text=decoded_text,
                )
            )

        return documents

    def search_documents(
        self,
        search: str,
        maximum_document_display_length: int,
        page: int,
        page_size: int,
    ) -> InfiniGramSearchResponse:
        tokenized_query_ids = self.tokenize(search)
        matching_documents = self.infini_gram_engine.find(input_ids=tokenized_query_ids)

        matching_documents_result = self.__handle_error(matching_documents)

        if (page * page_size) >= matching_documents_result["cnt"]:
            # Pagination standard is to return an empty array if we're out of bounds
            return InfiniGramSearchResponse(
                documents=[], total_documents=matching_documents_result["cnt"]
            )

        shard_and_rank_in_page = []
        shard = 0
        offset = page * page_size
        for _ in range(page_size):
            while (
                offset
                >= matching_documents_result["segment_by_shard"][shard][1]
                - matching_documents_result["segment_by_shard"][shard][0]
            ):
                offset -= (
                    matching_documents_result["segment_by_shard"][shard][1]
                    - matching_documents_result["segment_by_shard"][shard][0]
                )
                shard += 1
                if shard >= len(matching_documents_result["segment_by_shard"]):
                    break
            if shard >= len(matching_documents_result["segment_by_shard"]):
                # We have reached the end of results
                break
            shard_and_rank_in_page.append(
                {
                    "shard": shard,
                    "rank": matching_documents_result["segment_by_shard"][shard][0]
                    + offset,
                }
            )
            offset += 1

        docs = [
            self.get_document_by_rank(
                shard=shard_and_rank["shard"],
                rank=shard_and_rank["rank"],
                maximum_document_display_length=maximum_document_display_length,
            )
            for shard_and_rank in shard_and_rank_in_page
        ]

        return InfiniGramSearchResponse(
            documents=docs, total_documents=matching_documents_result["cnt"]
        )

    # Attribute doesn't return a high-level response, it just returns stuff from the engine. Use this inside a service instead of returning it directly
    def attribute(
        self,
        input: str,
        delimiters: List[str],
        allow_spans_with_partial_words: bool,
        minimum_span_length: int,
        maximum_frequency: int,
        maximum_span_density: float,
        span_ranking_method: SpanRankingMethod,
    ) -> InfiniGramAttributionResponse:
        input_ids = self.tokenize(input)

        delimiter_token_ids = self.tokenizer.tokenize_attribution_delimiters(delimiters)

        attribute_response = self.infini_gram_engine.attribute(
            input_ids=input_ids,
            delim_ids=delimiter_token_ids,
            min_len=minimum_span_length,
            max_cnt=maximum_frequency,
            enforce_bow=not allow_spans_with_partial_words,
        )

        # Limit the density of spans, and keep the longest ones
        maximum_num_spans = int(np.ceil(len(input_ids) * maximum_span_density))
        spans = attribute_response["spans"]
        if span_ranking_method == SpanRankingMethod.LENGTH:
            spans = sorted(spans, key=lambda x: x["length"], reverse=True)
        elif span_ranking_method == SpanRankingMethod.UNIGRAM_LOGPROB_SUM:
            spans = sorted(spans, key=lambda x: x["unigram_logprob_sum"], reverse=False)
        else:
            raise ValueError(f"Unknown span ranking method: {span_ranking_method}")
        spans = spans[:maximum_num_spans]
        spans = list(sorted(spans, key=lambda x: x["l"]))
        attribute_response["spans"] = spans

        attribute_result = self.__handle_error(attribute_response)

        return InfiniGramAttributionResponse(
            **attribute_result,
            index=self.index,
            input_token_ids=input_ids,
        )


indexes = {index: InfiniGramProcessor(index) for index in AvailableInfiniGramIndexId}


def InfiniGramProcessorFactoryPathParam(
    index: AvailableInfiniGramIndexId,
) -> InfiniGramProcessor:
    return indexes[index]


InfiniGramProcessorDependency = Annotated[
    InfiniGramProcessor, Depends(InfiniGramProcessorFactoryPathParam)
]
