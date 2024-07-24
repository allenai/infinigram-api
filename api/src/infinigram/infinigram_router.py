from typing import Annotated

from fastapi import APIRouter, Query

from src.infinigram.index_mappings import AvailableInfiniGramIndexId
from src.infinigram.processor import (
    InfiniGramCountResponse,
    InfiniGramProcessorDependency,
)

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
