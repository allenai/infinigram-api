from typing import Annotated, List

from fastapi import APIRouter, Body
from pydantic import Field

from src.camel_case_model import CamelCaseModel
from src.infinigram.index_mappings import AvailableInfiniGramIndexId
from src.infinigram.processor import (
    InfiniGramAttributionResponse,
    InfiniGramAttributionResponseWithDocs,
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
    return [index for index in AvailableInfiniGramIndexId]


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
    infini_gram_processor: InfiniGramProcessorFactoryBodyParamDependency,
) -> InfiniGramCountResponse:
    result = infini_gram_processor.count_n_gram(query=query)

    return result


@infinigram_router.get("/documents/{index}/{shard}/{rank}")
def rank(
    shard: int,
    rank: int,
    infini_gram_processor: InfiniGramProcessorFactoryPathParamDependency,
) -> InfiniGramRankResponse:
    result = infini_gram_processor.rank(shard=shard, rank=rank)

    return result


@infinigram_router.get("/documents/{index}")
def get_documents(
    infini_gram_processor: InfiniGramProcessorFactoryPathParamDependency,
    search: str,
) -> InfiniGramDocumentsResponse:
    result = infini_gram_processor.get_documents(search)

    return result


class AttributionRequest(CamelCaseModel):
    query: str = Field(examples=["This is a chat bot response"])
    delimiters: List[str] = Field(examples=[["\n", "."]], default=[])
    minimum_span_length: int = Field(gt=0, default=5)
    maximum_frequency: int = Field(gt=0, default=10)
    include_documents: bool = False


@infinigram_router.post(path="/{index}/attribution")
def get_document_attributions(
    body: AttributionRequest,
    infini_gram_processor: InfiniGramProcessorFactoryPathParamDependency,
) -> InfiniGramAttributionResponse | InfiniGramAttributionResponseWithDocs:
    result = infini_gram_processor.get_attribution_for_response(
        search=body.query,
        delimiters=body.delimiters,
        minimum_span_length=body.minimum_span_length,
        maximum_frequency=body.maximum_frequency,
        include_documents=body.include_documents,
    )

    return result
