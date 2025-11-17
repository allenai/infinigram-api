from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi_problem.handler import generate_swagger_response
from infini_gram_processor.index_mappings import AvailableInfiniGramIndexId

from src.attribution.attribution_request import AttributionRequest
from src.attribution.attribution_service import (
    AttributionResponse,
    AttributionService,
    AttributionTimeoutError,
)

attribution_router = APIRouter()


@attribution_router.post(
    path="/{index}/attribution",
    responses={
        AttributionTimeoutError.status: generate_swagger_response(
            AttributionTimeoutError  # type: ignore
        )
    },
)
async def get_document_attributions(
    index: AvailableInfiniGramIndexId,
    body: AttributionRequest,
    attribution_service: Annotated[AttributionService, Depends()],
) -> AttributionResponse:
    result = await attribution_service.get_attribution_for_response(index, body)

    return result
