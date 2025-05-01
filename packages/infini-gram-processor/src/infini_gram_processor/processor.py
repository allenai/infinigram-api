import json
from typing import (
    Iterable,
    Sequence,
    cast,
    List,
    Optional,
)

from infini_gram.engine import InfiniGramEngineDiff
from infini_gram.models import (
    InfiniGramEngineResponse,
)
from opentelemetry import trace
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
    GetDocumentByPointerGroupedRequest,
    InfiniGramAttributionResponse,
    CountCnfResponse,
    CountResponse,
    DistTokenResult,
    FindCnfResponse,
    FindResponse,
    InfgramNtdResponse,
    InfgramProbResponse,
    NtdResponse,
    ProbResponse,
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
            vocab_size=self.tokenizer.vocab_size,
            # for the attribution feature, disabling prefetching can speed things up
            ds_prefetch_depth=0,
            sa_prefetch_depth=0,
            od_prefetch_depth=0,
            bow_ids_path=self.tokenizer.bow_ids_path,
            attribution_block_size=256,
            precompute_unigram_logprobs=True,
        )

        self.MAX_QUERY_CHARS = 1000
        self.MAX_QUERY_TOKENS = 500
        self.MAX_CLAUSES_PER_CNF = 4
        self.MAX_TERMS_PER_CLAUSE = 4
        self.MAX_SUPPORT = 10000
        self.MAX_CLAUSE_FREQ = 500000
        self.MAX_DIFF_TOKENS = 1000

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
            raise InfiniGramEngineException(detail=result["error"])

        return cast(TInfiniGramResponse, result)

    def validate_and_tokenize_query(
        self, query: str | List[int]
    ) -> tuple[List[int], List[str]]:
        # this function checks the upper limits, but doesn't check anything else

        if isinstance(query, str):
            if len(query) > self.MAX_QUERY_CHARS:
                raise InfiniGramEngineException(
                    detail=f"Please limit your input to <= {self.MAX_QUERY_CHARS} characters!"
                )
            query_ids = self.tokenize(query)
        else:
            query_ids = query

        tokens = self.tokenizer.hf_tokenizer.convert_ids_to_tokens(query_ids)

        return query_ids, tokens

    def validate_and_tokenize_query_cnf(
        self, query: str | List[List[List[int]]]
    ) -> tuple[List[List[List[int]]], List[List[List[str]]]]:
        # this function checks the upper limits, but doesn't check anything else

        if isinstance(query, str):
            if len(query) > self.MAX_QUERY_CHARS:
                raise InfiniGramEngineException(
                    detail=f"Please limit your input to <= {self.MAX_QUERY_CHARS} characters!"
                )
            cnf = [
                [self.tokenize(term) for term in clause.split(" OR ")]
                for clause in query.split(" AND ")
            ]
        else:
            cnf = query

        if (
            sum(sum(len(term) for term in clause) for clause in cnf)
            > self.MAX_QUERY_TOKENS
        ):
            raise InfiniGramEngineException(
                detail=f"Please limit your input to <= {self.MAX_QUERY_TOKENS} tokens!"
            )
        if len(cnf) > self.MAX_CLAUSES_PER_CNF:
            raise InfiniGramEngineException(
                detail=f"Please enter at most {self.MAX_CLAUSES_PER_CNF} disjunctive clauses!"
            )
        for clause in cnf:
            if len(clause) > self.MAX_TERMS_PER_CLAUSE:
                raise InfiniGramEngineException(
                    detail=f"Please enter at most {self.MAX_TERMS_PER_CLAUSE} terms in each disjunctive clause!"
                )

        tokens = [
            [self.tokenizer.hf_tokenizer.convert_ids_to_tokens(term) for term in clause]
            for clause in cnf
        ]

        return cnf, tokens

    @tracer.start_as_current_span("infini_gram_processor/find")
    def find(
        self,
        query: str | List[int],
    ) -> FindResponse:
        query_ids, tokens = self.validate_and_tokenize_query(query)

        find_response = self.infini_gram_engine.find(input_ids=query_ids)

        find_result = self.__handle_error(find_response)

        return FindResponse(
            index=self.index, token_ids=query_ids, tokens=tokens, **find_result
        )

    @tracer.start_as_current_span("infini_gram_processor/find_cnf")
    def find_cnf(
        self,
        query: str | List[List[List[int]]],
        max_clause_freq: Optional[int] = None,
        max_diff_tokens: Optional[int] = None,
    ) -> FindCnfResponse:
        if max_clause_freq is not None and not (
            1 <= max_clause_freq <= self.MAX_CLAUSE_FREQ
        ):
            raise InfiniGramEngineException(
                detail=f"max_clause_freq must be an integer in [1, {self.MAX_CLAUSE_FREQ}]!"
            )
        if max_diff_tokens is not None and not (
            1 <= max_diff_tokens <= self.MAX_DIFF_TOKENS
        ):
            raise InfiniGramEngineException(
                detail=f"max_diff_tokens must be an integer in [1, {self.MAX_DIFF_TOKENS}]!"
            )

        cnf, tokens = self.validate_and_tokenize_query_cnf(query)

        find_cnf_response = self.infini_gram_engine.find_cnf(
            cnf=cnf, max_clause_freq=max_clause_freq, max_diff_tokens=max_diff_tokens
        )

        find_cnf_result = self.__handle_error(find_cnf_response)

        return FindCnfResponse(
            index=self.index, token_ids=cnf, tokens=tokens, **find_cnf_result
        )

    @tracer.start_as_current_span("infini_gram_processor/count")
    def count(self, query: str | List[int]) -> CountResponse:
        query_ids, tokens = self.validate_and_tokenize_query(query)

        count_response = self.infini_gram_engine.count(input_ids=query_ids)

        count_result = self.__handle_error(count_response)

        return CountResponse(
            index=self.index, token_ids=query_ids, tokens=tokens, **count_result
        )

    @tracer.start_as_current_span("infini_gram_processor/count_cnf")
    def count_cnf(
        self,
        query: str | List[List[List[int]]],
        max_clause_freq: Optional[int] = None,
        max_diff_tokens: Optional[int] = None,
    ) -> CountCnfResponse:
        if max_clause_freq is not None and not (
            1 <= max_clause_freq <= self.MAX_CLAUSE_FREQ
        ):
            raise InfiniGramEngineException(
                detail=f"max_clause_freq must be an integer in [1, {self.MAX_CLAUSE_FREQ}]!"
            )
        if max_diff_tokens is not None and not (
            1 <= max_diff_tokens <= self.MAX_DIFF_TOKENS
        ):
            raise InfiniGramEngineException(
                detail=f"max_diff_tokens must be an integer in [1, {self.MAX_DIFF_TOKENS}]!"
            )

        cnf, tokens = self.validate_and_tokenize_query_cnf(query)

        count_cnf_response = self.infini_gram_engine.count_cnf(
            cnf=cnf, max_clause_freq=max_clause_freq, max_diff_tokens=max_diff_tokens
        )

        count_cnf_result = self.__handle_error(count_cnf_response)

        return CountCnfResponse(
            index=self.index, token_ids=cnf, tokens=tokens, **count_cnf_result
        )

    @tracer.start_as_current_span("infini_gram_processor/prob")
    def prob(
        self,
        query: str | List[int],
    ) -> ProbResponse:
        query_ids, tokens = self.validate_and_tokenize_query(query)

        if len(query_ids) == 0:
            raise InfiniGramEngineException(detail="Query is empty")

        prob_response = self.infini_gram_engine.prob(
            prompt_ids=query_ids[:-1], cont_id=query_ids[-1]
        )

        prob_result = self.__handle_error(prob_response)

        return ProbResponse(
            index=self.index, token_ids=query_ids, tokens=tokens, **prob_result
        )

    @tracer.start_as_current_span("infini_gram_processor/ntd")
    def ntd(
        self,
        query: str | List[int],
        max_support: Optional[int] = None,
    ) -> NtdResponse:
        if max_support is not None and not (1 <= max_support <= self.MAX_SUPPORT):
            raise InfiniGramEngineException(
                detail=f"max_support must be an integer in [1, {self.MAX_SUPPORT}]!"
            )

        query_ids, tokens = self.validate_and_tokenize_query(query)

        ntd_response = self.infini_gram_engine.ntd(
            prompt_ids=query_ids, max_support=max_support
        )

        ntd_result = self.__handle_error(ntd_response)

        if "result_by_token_id" in ntd_result:
            result_by_token_id = {
                token_id: DistTokenResult(
                    cont_cnt=result["cont_cnt"],
                    prob=result["prob"],
                    token=self.tokenizer.hf_tokenizer.convert_ids_to_tokens([token_id])[
                        0
                    ],
                )
                for token_id, result in ntd_result["result_by_token_id"].items()
            }
            return NtdResponse(
                index=self.index,
                token_ids=query_ids,
                tokens=tokens,
                prompt_cnt=ntd_result["prompt_cnt"],
                result_by_token_id=result_by_token_id,
                approx=ntd_result["approx"],
            )

        return NtdResponse(
            index=self.index, token_ids=query_ids, tokens=tokens, **ntd_result
        )

    @tracer.start_as_current_span("infini_gram_processor/infgram_prob")
    def infgram_prob(
        self,
        query: str | List[int],
    ) -> InfgramProbResponse:
        query_ids, tokens = self.validate_and_tokenize_query(query)

        infgram_prob_response = self.infini_gram_engine.infgram_prob(
            prompt_ids=query_ids[:-1], cont_id=query_ids[-1]
        )

        infgram_prob_result = self.__handle_error(infgram_prob_response)

        if "suffix_len" in infgram_prob_result:
            longest_suffix = self.tokenizer.hf_tokenizer.decode(
                query_ids[-infgram_prob_result["suffix_len"] - 1 : -1],
                skip_special_tokens=False,
                clean_up_tokenization_spaces=False,
            )
            return InfgramProbResponse(
                index=self.index,
                token_ids=query_ids,
                tokens=tokens,
                prompt_cnt=infgram_prob_result["prompt_cnt"],
                cont_cnt=infgram_prob_result["cont_cnt"],
                prob=infgram_prob_result["prob"],
                suffix_len=infgram_prob_result["suffix_len"],
                longest_suffix=longest_suffix,
            )

        return InfgramProbResponse(
            index=self.index, token_ids=query_ids, tokens=tokens, **infgram_prob_result
        )

    @tracer.start_as_current_span("infini_gram_processor/infgram_ntd")
    def infgram_ntd(
        self,
        query: str | List[int],
        max_support: Optional[int] = None,
    ) -> InfgramNtdResponse:
        if max_support is not None and not (1 <= max_support <= self.MAX_SUPPORT):
            raise InfiniGramEngineException(
                detail=f"max_support must be an integer in [1, {self.MAX_SUPPORT}]!"
            )

        query_ids, tokens = self.validate_and_tokenize_query(query)

        infgram_ntd_response = self.infini_gram_engine.infgram_ntd(
            prompt_ids=query_ids, max_support=max_support
        )

        infgram_ntd_result = self.__handle_error(infgram_ntd_response)

        if "result_by_token_id" in infgram_ntd_result:
            result_by_token_id = {
                token_id: DistTokenResult(
                    cont_cnt=result["cont_cnt"],
                    prob=result["prob"],
                    token=self.tokenizer.hf_tokenizer.convert_ids_to_tokens([token_id])[
                        0
                    ],
                )
                for token_id, result in infgram_ntd_result["result_by_token_id"].items()
            }
            longest_suffix = self.tokenizer.hf_tokenizer.decode(
                query_ids[-infgram_ntd_result["suffix_len"] :],
                skip_special_tokens=False,
                clean_up_tokenization_spaces=False,
            )
            return InfgramNtdResponse(
                index=self.index,
                token_ids=query_ids,
                tokens=tokens,
                prompt_cnt=infgram_ntd_result["prompt_cnt"],
                result_by_token_id=result_by_token_id,
                approx=infgram_ntd_result["approx"],
                suffix_len=infgram_ntd_result["suffix_len"],
                longest_suffix=longest_suffix,
            )

        return InfgramNtdResponse(
            index=self.index, token_ids=query_ids, tokens=tokens, **infgram_ntd_result
        )

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
        document_requests: Iterable[GetDocumentByPointerRequest],
    ) -> list[Document]:
        get_docs_by_pointers_response = self.infini_gram_engine.get_docs_by_ptrs_2(
            requests=[
                (
                    document_request.shard,
                    document_request.pointer,
                    document_request.needle_length,
                    document_request.maximum_context_length,
                )
                for document_request in document_requests
            ],
        )

        documents_result = self.__handle_error(get_docs_by_pointers_response)

        return [
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

    @tracer.start_as_current_span(
        "infini_gram_processor/get_documents_by_pointers_grouped"
    )
    def get_documents_by_pointers_grouped(
        self,
        document_request_by_span: Iterable[GetDocumentByPointerGroupedRequest],
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
