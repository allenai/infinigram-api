from typing import Iterable

from infini_gram.engine import InfiniGramEngine
from pydantic import BaseModel
from transformers import AutoTokenizer, PreTrainedTokenizerBase


class Document(BaseModel):
    disp_len: int
    doc_ix: int
    doc_len: int
    metadata: str
    token_ids: Iterable[int]


class InfiniGramQueryResponse(BaseModel):
    approx: bool
    cnt: int
    documents: Iterable[Document]
    idxs: Iterable[int]

class InfiniGramCountResponse(BaseModel):
    approx: bool
    count: int


class InfiniGramProcessor:
    tokenizer: PreTrainedTokenizerBase
    infini_gram_engine: InfiniGramEngine

    def __init__(self):
        self.tokenizer = AutoTokenizer.from_pretrained(
            "./vendor/llama-2-7b-hf/", add_bos_token=False, add_eos_token=False
        )

        self.infini_gram_engine = InfiniGramEngine(
            index_dir="/mnt/infinigram-array", eos_token_id=self.tokenizer.eos_token_id
        )

    def find_docs_with_query(self, query: str) -> InfiniGramQueryResponse:
        tokenized_query_ids = self.tokenizer.encode(query)
        return self.infini_gram_engine.search_docs(
            input_ids=tokenized_query_ids, maxnum=1, max_disp_len=10
        )
    
    def count_n_gram(self, query: str) -> InfiniGramCountResponse:
        tokenized_query_ids = self.tokenizer.encode(query)
        return self.infini_gram_engine.count(input_ids=tokenized_query_ids)


processor = InfiniGramProcessor()
