from typing import Annotated

from fastapi import APIRouter, Body

from src.infinigram.index_mappings import AvailableInfiniGramIndexId
from src.infinigram.processor import (
    InfiniGramCountResponse,
    InfiniGramDocumentsResponse,
    InfiniGramProcessorFactoryBodyParamDependency,
    InfiniGramProcessorFactoryPathParamDependency,
    InfiniGramQueryResponse,
    InfiniGramRankResponse,
)

infinigram_router = APIRouter()


@infinigram_router.get(path="/indexes")
def get_available_indexes() -> list[AvailableInfiniGramIndexId]:
    return [index_id for index_id in AvailableInfiniGramIndexId]


@infinigram_router.post("/query")
def query(
    query: Annotated[
        str, Body(examples=["Seattle", "Economic Growth", "Linda Tuhiwai Smith"])
    ],
    infini_gram_processor: InfiniGramProcessorFactoryBodyParamDependency,
) -> InfiniGramQueryResponse:
    result = infini_gram_processor.find_docs_with_query(query=query)

    return result


@infinigram_router.post("/count")
def count(
    query: Annotated[str, Body(examples=["Seattle"])],
    index_id: Annotated[AvailableInfiniGramIndexId, Body()],
    infini_gram_processor: InfiniGramProcessorFactoryBodyParamDependency,
) -> InfiniGramCountResponse:
    result = infini_gram_processor.count_n_gram(query=query)

    return result


@infinigram_router.get("/documents/{index_id}/{shard}/{rank}")
def rank(
    shard: int,
    rank: int,
    infini_gram_processor: InfiniGramProcessorFactoryPathParamDependency,
) -> InfiniGramRankResponse:
    result = infini_gram_processor.rank(shard=shard, rank=rank)

    return result


@infinigram_router.get("/documents/{index_id}")
def get_documents(
    infini_gram_processor: InfiniGramProcessorFactoryPathParamDependency,
    search: str,
) -> InfiniGramDocumentsResponse:
    result = infini_gram_processor.get_documents(search)

    return result
