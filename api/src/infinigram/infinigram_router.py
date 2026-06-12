from fastapi import APIRouter
from infini_gram_processor.index_mappings import AvailableInfiniGramIndexId
from infini_gram_processor.models.models import (
    CountCnfRequest,
    CountCnfResponse,
    CountRequest,
    CountResponse,
)

from src.infinigram.count_service import CountServiceDependency

infinigram_router = APIRouter()


@infinigram_router.get(path="/indexes")
def get_available_indexes() -> list[AvailableInfiniGramIndexId]:
    return [index for index in AvailableInfiniGramIndexId]


@infinigram_router.post("/{index}/count")
async def count(
    index: AvailableInfiniGramIndexId,
    body: CountRequest,
    count_service: CountServiceDependency,
) -> CountResponse:
    """
    This query type counts the number of times the query string appears in the corpus. If the query is an empty string, the total number of tokens in the corpus will be returned.

    For more info, see the infini-gram package docs: https://infini-gram.readthedocs.io/en/latest/pkg.html#count-an-n-gram-or-a-cnf-of-multiple-n-grams
    """

    return await count_service.count(index, body)


@infinigram_router.post("/{index}/count_cnf")
async def count_cnf(
    index: AvailableInfiniGramIndexId,
    body: CountCnfRequest,
    count_service: CountServiceDependency,
) -> CountCnfResponse:
    """
    This query type counts the number of times the query string appears in the corpus. If the query is an empty string, the total number of tokens in the corpus will be returned.

    You can simply enter a string, in which we count the number of occurrences of the string. You can also connect multiple strings with the AND/OR operators, in the CNF format, in which case we count the number of times where this logical constraint is satisfied.

    For more info, see the infini-gram package docs: https://infini-gram.readthedocs.io/en/latest/pkg.html#count-an-n-gram-or-a-cnf-of-multiple-n-grams
    """

    return await count_service.count_cnf(index, body)
