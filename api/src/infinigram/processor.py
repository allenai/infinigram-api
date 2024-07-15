import json
from typing import Annotated, Any, Iterable, List

from fastapi import Body, Depends
from infini_gram.engine import InfiniGramEngine  # type: ignore
from pydantic import Field
from transformers import AutoTokenizer, PreTrainedTokenizerBase  # type: ignore

from src.camel_case_model import CamelCaseModel
from src.infinigram.index_mappings import AvailableInfiniGramIndexId, index_mappings
from src.infinigram.infini_gram_engine_exception import InfiniGramEngineException


class BaseInfiniGramResponse(CamelCaseModel):
    index: str


class InfiniGramErrorResponse(CamelCaseModel):
    error: str


class Document(CamelCaseModel):
    disp_len: int
    doc_ix: int
    doc_len: int
    metadata: str
    token_ids: Iterable[int]


class InfiniGramQueryResponse(BaseInfiniGramResponse):
    approx: bool
    count: int = Field(validation_alias="cnt")
    documents: Iterable[Document]
    indexes: Iterable[int] = Field(validation_alias="idxs")


class InfiniGramCountResponse(BaseInfiniGramResponse):
    approx: bool
    count: int


class InfiniGramRankResponse(BaseInfiniGramResponse):
    document_index: int = Field(validation_alias="doc_ix")
    document_length: int = Field(validation_alias="doc_len")
    display_length: int = Field(validation_alias="disp_len")
    metadata: dict[str, str] = Field(validation_alias="parsed_metadata")
    token_ids: Iterable[int]
    text: str


class InfiniGramDocumentsResponse(BaseInfiniGramResponse):
    documents: Iterable[InfiniGramRankResponse]


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

        self.infini_gram_engine = InfiniGramEngine(
            index_dir=index_mapping["index_dir"],
            eos_token_id=self.tokenizer.eos_token_id,
        )

    def __tokenize(self, query: str) -> Iterable[int]:
        # mypy didn't think this was always a list for some reason, hence the forced type
        encoded_query: List[int] = self.tokenizer.encode(query)
        return encoded_query

    def __handleError(self, result: dict[str, Any]) -> None:
        if "error" in result:
            raise InfiniGramEngineException(detail=result["error"])

    def find_docs_with_query(self, query: str) -> InfiniGramQueryResponse:
        tokenized_query_ids = self.__tokenize(query)

        docs_result = self.infini_gram_engine.search_docs(
            input_ids=tokenized_query_ids, maxnum=1, max_disp_len=10
        )

        self.__handleError(docs_result)

        return InfiniGramQueryResponse(index=self.index, **docs_result)

    def count_n_gram(self, query: str) -> InfiniGramCountResponse:
        tokenized_query_ids = self.__tokenize(query)

        count_result = self.infini_gram_engine.count(input_ids=tokenized_query_ids)

        self.__handleError(count_result)

        return InfiniGramCountResponse(index=self.index, **count_result)

    def rank(self, shard: int, rank: int) -> InfiniGramRankResponse:
        get_doc_by_rank_response = self.infini_gram_engine.get_doc_by_rank(
            s=shard, rank=rank, max_disp_len=10
        )

        self.__handleError(get_doc_by_rank_response)

        parsed_metadata = json.loads(get_doc_by_rank_response["metadata"])
        decoded_text = self.tokenizer.decode(get_doc_by_rank_response["token_ids"])

        return InfiniGramRankResponse(
            index=self.index,
            # parsed_metadata resolves to metadata with a validation alias
            parsed_metadata=parsed_metadata,  # type: ignore
            text=decoded_text,
            **get_doc_by_rank_response,
        )

    def get_documents(self, search: str) -> InfiniGramDocumentsResponse:
        tokenized_query_ids = self.__tokenize(search)
        matching_documents = self.infini_gram_engine.find(input_ids=tokenized_query_ids)

        self.__handleError(matching_documents)

        docs = []
        for s, (start, end) in enumerate(matching_documents["segment_by_shard"]):
            for rank in range(start, end):
                doc = self.rank(shard=s, rank=rank)
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
