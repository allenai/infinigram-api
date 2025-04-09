from fastapi import APIRouter
from infini_gram_processor.index_mappings import AvailableInfiniGramIndexId

infinigram_router = APIRouter()


@infinigram_router.get(path="/indexes")
def get_available_indexes() -> list[AvailableInfiniGramIndexId]:
    return [index for index in AvailableInfiniGramIndexId]
