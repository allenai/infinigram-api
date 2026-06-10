from fastapi import APIRouter
from infini_gram_processor.index_mappings import AvailableInfiniGramIndexId
from infini_gram_processor.models.models import CountCnfRequest, CountRequest

from api.src.infinigram.count_service import CountServiceDependency

infinigram_router = APIRouter()


@infinigram_router.get(path="/indexes")
def get_available_indexes() -> list[AvailableInfiniGramIndexId]:
    return [index for index in AvailableInfiniGramIndexId]


@infinigram_router.post("/{index}/count")
async def count(
    index: AvailableInfiniGramIndexId,
    body: CountRequest,
    count_service: CountServiceDependency,
):
    return await count_service.count(index, body)


@infinigram_router.post("/{index}/count_cnf")
def count_cnf(
    index: AvailableInfiniGramIndexId,
    body: CountCnfRequest,
    count_service: CountServiceDependency,
): ...
