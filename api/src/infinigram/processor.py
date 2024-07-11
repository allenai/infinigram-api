from typing import Annotated, Iterable

from fastapi import Body, Depends
from infini_gram.engine import InfiniGramEngine
from pydantic import BaseModel, Field
from transformers import AutoTokenizer, PreTrainedTokenizerBase

from src.infinigram.index_mappings import AvailableInfiniGramIndexId, index_mappings


class BaseInfiniGramResponse(BaseModel):
    index_id: str


class Document(BaseModel):
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


class InfiniGramProcessor:
    index_id: str
    tokenizer: PreTrainedTokenizerBase
    infini_gram_engine: InfiniGramEngine

    def __init__(self, index_id: AvailableInfiniGramIndexId):
        self.index_id = index_id.value
        index_mapping = index_mappings[index_id.value]

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

    def __tokenize(self, query) -> Iterable[int]:
        return self.tokenizer.encode(query)

    def find_docs_with_query(self, query: str) -> InfiniGramQueryResponse:
        tokenized_query_ids = self.__tokenize(query)

        docs_result = self.infini_gram_engine.search_docs(
            input_ids=tokenized_query_ids, maxnum=1, max_disp_len=10
        )

        return InfiniGramQueryResponse(index_id=self.index_id, **docs_result)

    def count_n_gram(self, query: str) -> InfiniGramCountResponse:
        tokenized_query_ids = self.__tokenize(query)

        count_result = self.infini_gram_engine.count(input_ids=tokenized_query_ids)

        return InfiniGramCountResponse(index_id=self.index_id, **count_result)


indexes = {index: InfiniGramProcessor(index) for index in AvailableInfiniGramIndexId}


def InfiniGramProcessorFactory(
    index_id: AvailableInfiniGramIndexId = Body(),
) -> InfiniGramProcessor:
    return indexes[index_id]


InfiniGramProcessorFactoryDependency = Annotated[
    InfiniGramProcessor, Depends(InfiniGramProcessorFactory)
]
