import json
from typing import (
    Iterable,
    Sequence,
    cast,
)

from infini_gram.engine import InfiniGramEngineDiff
from infini_gram.models import (
    InfiniGramEngineResponse,
)
from opentelemetry import trace
from opentelemetry.trace.status import StatusCode
from transformers.tokenization_utils_base import (  # type: ignore
    EncodedInput,
    PreTokenizedInput,
    TextInput,
)

from .index_mappings import AvailableInfiniGramIndexId, index_mappings
from .infini_gram_engine_exception import InfiniGramEngineException
from .models import (
    Document,
    GetDocumentByIndexRequest,
    GetDocumentByPointerRequest,
    GetDocumentByRankRequest,
    InfiniGramAttributionResponse,
    InfiniGramCountResponse,
    InfiniGramSearchResponse,
)
from .models.is_infini_gram_error_response import (
    TInfiniGramResponse,
    is_infini_gram_error_response,
)
from .tokenizers.tokenizer import Tokenizer

tracer = trace.get_tracer(__name__)


class InfiniGramProcessor:
    index: str
    tokenizer: Tokenizer
    infini_gram_engine: InfiniGramEngineDiff

    def __init__(self, index: AvailableInfiniGramIndexId):
        self.index = index.value
        index_mapping = index_mappings[index.value]

        self.tokenizer = index_mapping["tokenizer"]

        self.infini_gram_engine = InfiniGramEngineDiff(
            index_dir=index_mapping["index_dir"],
            index_dir_diff=index_mapping["index_dir_diff"],
            eos_token_id=self.tokenizer.eos_token_id,
            bow_ids_path=self.tokenizer.bow_ids_path,  # type:ignore
            # We need to get the OSX build of infini-gram working again so we can upgrade it to 2.5.0
            attribution_block_size=256,
            precompute_unigram_logprobs=True,
            # for the attribution feature, disabling prefetching can speed things up
            ds_prefetch_depth=0,
            sa_prefetch_depth=0,
            od_prefetch_depth=0,
            vocab_size=self.tokenizer.hf_tokenizer.vocab_size,
            token_dtype="u32",
        )

    @tracer.start_as_current_span("infini_gram_processor/tokenize")
    def tokenize(
        self, input: TextInput | PreTokenizedInput | EncodedInput
    ) -> list[int]:
        return self.tokenizer.tokenize(input)

    @tracer.start_as_current_span("infini_gram_processor/decode_tokens")
    def decode_tokens(self, token_ids: Iterable[int]) -> str:
        return self.tokenizer.decode_tokens(token_ids)

    @tracer.start_as_current_span("infini_gram_processor/tokenize_to_list")
    def tokenize_to_list(self, input: TextInput) -> Sequence[str]:
        return self.tokenizer.tokenize_to_list(input)

    def __handle_error(
        self,
        result: InfiniGramEngineResponse[TInfiniGramResponse],
    ) -> TInfiniGramResponse:
        if is_infini_gram_error_response(result):
            exception = InfiniGramEngineException(detail=result["error"])

            current_span = trace.get_current_span()
            current_span.record_exception(
                exception, attributes={"detail": exception.detail}
            )
            current_span.set_status(StatusCode.ERROR)

            raise exception

        return cast(TInfiniGramResponse, result)

    @tracer.start_as_current_span("infini_gram_processor/count_n_gram")
    def count_n_gram(self, query: str) -> InfiniGramCountResponse:
        tokenized_query_ids = self.tokenize(query)

        count_response = self.infini_gram_engine.count(input_ids=tokenized_query_ids)

        count_result = self.__handle_error(count_response)

        return InfiniGramCountResponse(index=self.index, **count_result)

    @tracer.start_as_current_span("infini_gram_processor/get_document_by_rank")
    def get_document_by_rank(
        self, shard: int, rank: int, needle_length: int, maximum_context_length: int
    ) -> Document:
        get_doc_by_rank_response = self.infini_gram_engine.get_doc_by_rank_2(
            s=shard,
            rank=rank,
            needle_len=needle_length,
            max_ctx_len=maximum_context_length,
        )

        document_result = self.__handle_error(get_doc_by_rank_response)

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

    @tracer.start_as_current_span("infini_gram_processor/get_documents_by_ranks")
    def get_documents_by_ranks(
        self,
        document_requests: Iterable[GetDocumentByRankRequest],
    ) -> list[Document]:
        get_docs_by_ranks_response = self.infini_gram_engine.get_docs_by_ranks_2(
            requests=[
                (
                    document_request.shard,
                    document_request.rank,
                    document_request.needle_length,
                    document_request.maximum_context_length,
                )
                for document_request in document_requests
            ],
        )

        document_results = self.__handle_error(get_docs_by_ranks_response)

        documents = []
        for document_result in document_results:
            parsed_metadata = json.loads(document_result["metadata"])
            decoded_text = self.decode_tokens(document_result["token_ids"])

            documents.append(
                Document(
                    document_index=document_result["doc_ix"],
                    document_length=document_result["doc_len"],
                    display_length=document_result["disp_len"],
                    needle_offset=document_result["needle_offset"],
                    metadata=parsed_metadata,
                    token_ids=document_result["token_ids"],
                    text=decoded_text,
                )
            )

        return documents

    @tracer.start_as_current_span("infini_gram_processor/get_document_by_pointer")
    def get_document_by_pointer(
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

    @tracer.start_as_current_span("infini_gram_processor/get_documents_by_pointers")
    def get_documents_by_pointers(
        self,
        document_request_by_span: Iterable[GetDocumentByPointerRequest],
    ) -> list[list[Document]]:
        get_docs_by_pointers_response = (
            self.infini_gram_engine.get_docs_by_ptrs_2_grouped(
                requests=[
                    {
                        "docs": document_request.docs,
                        "span_ids": document_request.span_ids,
                        "needle_len": document_request.needle_length,
                        "max_ctx_len": document_request.maximum_context_length,
                    }
                    for document_request in document_request_by_span
                ],
            )
        )

        documents_by_span_result = self.__handle_error(get_docs_by_pointers_response)

        return [
            [
                Document(
                    document_index=document_result["doc_ix"],
                    document_length=document_result["doc_len"],
                    display_length=document_result["disp_len"],
                    needle_offset=document_result["needle_offset"],
                    metadata=json.loads(document_result["metadata"]),
                    token_ids=document_result["token_ids"],
                    text=self.decode_tokens(document_result["token_ids"]),
                    blocked=document_result["blocked"],
                )
                for document_result in documents_result
            ]
            for documents_result in documents_by_span_result
        ]

    @tracer.start_as_current_span("infini_gram_processor/get_document_by_index")
    def get_document_by_index(
        self, document_index: int, maximum_context_length: int
    ) -> Document:
        get_doc_by_index_response = self.infini_gram_engine.get_doc_by_ix_2(
            doc_ix=document_index,
            max_ctx_len=maximum_context_length,
        )

        document_result = self.__handle_error(get_doc_by_index_response)

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

    @tracer.start_as_current_span("infini_gram_processor/get_documents_by_indexes")
    def get_documents_by_indexes(
        self, document_requests: Iterable[GetDocumentByIndexRequest]
    ) -> list[Document]:
        get_docs_by_indexes_response = self.infini_gram_engine.get_docs_by_ixs_2(
            requests=[
                (
                    document_request.document_index,
                    document_request.maximum_context_length,
                )
                for document_request in document_requests
            ],
        )

        document_results = self.__handle_error(get_docs_by_indexes_response)

        documents = []
        for document_result in document_results:
            parsed_metadata = json.loads(document_result["metadata"])
            decoded_text = self.decode_tokens(document_result["token_ids"])

            documents.append(
                Document(
                    document_index=document_result["doc_ix"],
                    document_length=document_result["doc_len"],
                    display_length=document_result["disp_len"],
                    needle_offset=document_result["needle_offset"],
                    metadata=parsed_metadata,
                    token_ids=document_result["token_ids"],
                    text=decoded_text,
                )
            )

        return documents

    @tracer.start_as_current_span("infini_gram_processor/search_documents")
    def search_documents(
        self,
        search: str,
        maximum_context_length: int,
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

        document_requests = []
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
            document_requests.append(
                GetDocumentByRankRequest(
                    shard=shard,
                    rank=matching_documents_result["segment_by_shard"][shard][0]
                    + offset,
                    needle_length=len(tokenized_query_ids),
                    maximum_context_length=maximum_context_length,
                )
            )
            offset += 1

        docs = self.get_documents_by_ranks(
            document_requests=document_requests,
        )

        return InfiniGramSearchResponse(
            documents=docs, total_documents=matching_documents_result["cnt"]
        )

    @tracer.start_as_current_span("infini_gram_processor/attribute")
    # Attribute doesn't return a high-level response, it just returns stuff from the engine. Use this inside a service instead of returning it directly
    def attribute(
        self,
        input: str,
        delimiters: list[str],
        allow_spans_with_partial_words: bool,
        minimum_span_length: int,
        maximum_frequency: int,
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

        attribute_result = self.__handle_error(attribute_response)

        return InfiniGramAttributionResponse(
            **attribute_result,
            index=self.index,
            input_token_ids=input_ids,
        )


indexes = {index: InfiniGramProcessor(index) for index in AvailableInfiniGramIndexId}
