import sys
import traceback
from typing import Annotated, Union

from fastapi import APIRouter, Body, HTTPException

from src.infinigram.index_mappings import AvailableInfiniGramIndexId
from src.infinigram.processor import (
    InfiniGramCountResponse,
    InfiniGramDocumentsResponse,
    InfiniGramErrorResponse,
    InfiniGramProcessorFactoryBodyParamDependency,
    InfiniGramProcessorFactoryPathParamDependency,
    InfiniGramQueryResponse,
    InfiniGramRankResponse,
)

infinigram_router = APIRouter()


@infinigram_router.get(path="/indexes")
def get_available_indexes() -> list[AvailableInfiniGramIndexId]:
    return [index for index in AvailableInfiniGramIndexId]


@infinigram_router.post("/query")
def query(
    query: Annotated[
        str, Body(examples=["Seattle", "Economic Growth", "Linda Tuhiwai Smith"])
    ],
    infini_gram_processor: InfiniGramProcessorFactoryBodyParamDependency,
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
    infini_gram_processor: InfiniGramProcessorFactoryBodyParamDependency,
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


@infinigram_router.get("/documents/{index}/{shard}/{rank}")
def rank(
    shard: int,
    rank: int,
    infini_gram_processor: InfiniGramProcessorFactoryPathParamDependency,
) -> Union[InfiniGramRankResponse, InfiniGramErrorResponse]:
    try:
        result = infini_gram_processor.rank(shard=shard, rank=rank)

        return result
    except Exception as e:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        traceback.print_exception(exc_type, exc_value, exc_traceback)

        raise HTTPException(
            status_code=500, detail=f"[FastAPI] Internal server error: {e}"
        )


@infinigram_router.get("/documents/{index}")
def get_documents(
    infini_gram_processor: InfiniGramProcessorFactoryPathParamDependency,
    search: str | None = None,
) -> Union[InfiniGramDocumentsResponse, InfiniGramErrorResponse]:
    try:
        result = infini_gram_processor.get_documents(search)

        return result
    except Exception as e:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        traceback.print_exception(exc_type, exc_value, exc_traceback)

        raise HTTPException(
            status_code=500, detail=f"[FastAPI] Internal server error: {e}"
        )
