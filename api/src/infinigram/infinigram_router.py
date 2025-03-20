from typing import Annotated

from fastapi import APIRouter, Query
from infini_gram_processor.index_mappings import AvailableInfiniGramIndexId
from infini_gram_processor.processor import (
    InfiniGramCountResponse,
)

from src.infinigram.infini_gram_dependency import InfiniGramProcessorDependency

infinigram_router = APIRouter()


@infinigram_router.get(path="/indexes")
def get_available_indexes() -> list[AvailableInfiniGramIndexId]:
    return [index for index in AvailableInfiniGramIndexId]


@infinigram_router.get("/{index}/count")
def count(
    query: Annotated[str, Query(examples=["Seattle"])],
    infini_gram_processor: InfiniGramProcessorDependency,
) -> InfiniGramCountResponse:
    result = infini_gram_processor.count_n_gram(query=query)

    return result
