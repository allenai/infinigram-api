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
    InfiniGramProcessorDependency,
    InfiniGramQueryResponse,
    InfiniGramRankResponse,
)

infinigram_router = APIRouter()


@infinigram_router.get(path="/indexes")
def get_available_indexes() -> list[AvailableInfiniGramIndexId]:
    return [index for index in AvailableInfiniGramIndexId]


@infinigram_router.post("/{index}/query")
def query(
    query: Annotated[
        str, Body(examples=["Seattle", "Economic Growth", "Linda Tuhiwai Smith"])
    ],
    infini_gram_processor: InfiniGramProcessorDependency,
) -> InfiniGramQueryResponse:
    result = infini_gram_processor.find_docs_with_query(query=query)

    return result


@infinigram_router.post("/{index}/count")
def count(
    query: Annotated[str, Body(examples=["Seattle"])],
    infini_gram_processor: InfiniGramProcessorDependency,
) -> InfiniGramCountResponse:
    result = infini_gram_processor.count_n_gram(query=query)

    return result


@infinigram_router.get("/{index}/documents/{shard}/{rank}")
def rank(
    shard: int,
    rank: int,
    infini_gram_processor: InfiniGramProcessorDependency,
) -> InfiniGramRankResponse:
    result = infini_gram_processor.rank(shard=shard, rank=rank)

    return result


@infinigram_router.get("/{index}/documents/")
def get_documents(
    infini_gram_processor: InfiniGramProcessorDependency,
    search: str,
) -> InfiniGramDocumentsResponse:
    result = infini_gram_processor.get_documents(search)

    return result


EXAMPLE_ATTRIBUTION_QUERY = "Hailing a taxi in Rome is fairly easy. Expect to pay around EUR 10-15 (approx. $11.29 - $15.58) to most tourist spots. Tipping isn't common in Italy, but round up the taxi fare or leave a small tip in the event of exceptional service. car rental is an alternative, but traffic in Rome can be daunting for newbies. If you decide to rent a car, make sure you're comfortable navigating busy medieval streets."


class AttributionRequest(CamelCaseModel):
    query: str = Field(examples=[EXAMPLE_ATTRIBUTION_QUERY])
    delimiters: List[str] = Field(examples=[["\n", "."]], default=[])
    minimum_span_length: int = Field(gt=0, default=5)
    maximum_frequency: int = Field(gt=0, default=10)
    include_documents: bool = False
    maximum_document_display_length: int = Field(gt=0, default=100)


@infinigram_router.post(path="/{index}/attribution")
def get_document_attributions(
    body: AttributionRequest,
    infini_gram_processor: InfiniGramProcessorDependency,
) -> InfiniGramAttributionResponse | InfiniGramAttributionResponseWithDocs:
    result = infini_gram_processor.get_attribution_for_response(
        search=body.query,
        delimiters=body.delimiters,
        minimum_span_length=body.minimum_span_length,
        maximum_frequency=body.maximum_frequency,
        include_documents=body.include_documents,
        maximum_document_display_length=body.maximum_document_display_length,
    )

    return result
