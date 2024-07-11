import sys
import traceback
from typing import Annotated

from fastapi import APIRouter, Body, HTTPException

from src.infinigram.index_mappings import AvailableInfiniGramIndexId
from src.infinigram.processor import (
    InfiniGramCountResponse,
    InfiniGramProcessorFactoryDependency,
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
    infini_gram_processor: InfiniGramProcessorFactoryDependency,
) -> InfiniGramQueryResponse:
    try:
        result = infini_gram_processor.find_docs_with_query(query=query)

        return result
    except Exception as e:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        traceback.print_exception(exc_type, exc_value, exc_traceback)

        raise HTTPException(
            status_code=500, detail=f"[FastAPI] Internal server error: {e}"
        )


@infinigram_router.post("/count")
def count(
    query: Annotated[str, Body(examples=["Seattle"])],
    infini_gram_processor: InfiniGramProcessorFactoryDependency,
) -> InfiniGramCountResponse:
    try:
        result = infini_gram_processor.count_n_gram(query=query)

        return result
    except Exception as e:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        traceback.print_exception(exc_type, exc_value, exc_traceback)

        raise HTTPException(
            status_code=500, detail=f"[FastAPI] Internal server error: {e}"
        )

@infinigram_router.post("/document/{index}/{shard}/{rank}")
def rank(index: str, shard: int, rank: int) -> InfiniGramRankResponse:
        try: 
            result = processor.rank(shard=shard, rank=rank)

            return result
        except Exception as e:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_traceback)

            raise HTTPException(
                status_code=500, detail=f"[FastAPI] Internal server error: {e}"
            )