import json
from typing import Annotated, Any, Iterable, List, TypeGuard, TypeVar, cast

from fastapi import Body, Depends
from infini_gram.engine import InfiniGramEngine
from infini_gram.models import ErrorResponse, InfiniGramEngineResponse
from pydantic import Field
from transformers import AutoTokenizer, PreTrainedTokenizerBase

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

    def __tokenize(self, query: str) -> Iterable[int]:
        # mypy didn't think this was always a list for some reason, hence the forced type
        encoded_query: List[int] = self.tokenizer.encode(query)
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


indexes = {index: InfiniGramProcessor(index) for index in AvailableInfiniGramIndexId}


# TODO: See if we can simplify these
def InfiniGramProcessorFactoryPathParam(
    index: AvailableInfiniGramIndexId,
) -> InfiniGramProcessor:
    return indexes[index]


InfiniGramProcessorFactoryPathParamDependency = Annotated[
    InfiniGramProcessor, Depends(InfiniGramProcessorFactoryPathParam)
]


def InfiniGramProcessorFactoryBodyParam(
    index: AvailableInfiniGramIndexId = Body(),
) -> InfiniGramProcessor:
    return indexes[index]


InfiniGramProcessorFactoryBodyParamDependency = Annotated[
    InfiniGramProcessor, Depends(InfiniGramProcessorFactoryBodyParam)
]
