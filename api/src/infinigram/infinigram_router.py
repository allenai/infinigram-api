from fastapi import APIRouter
from infini_gram_processor.index_mappings import AvailableInfiniGramIndexId
from infini_gram_processor.models import (
    InfiniGramFindRequest,
    FindResponse,
    InfiniGramFindCnfRequest,
    FindCnfResponse,
    InfiniGramCountRequest,
    CountResponse,
    InfiniGramCountCnfRequest,
    CountCnfResponse,
    InfiniGramProbRequest,
    ProbResponse,
    InfiniGramNtdRequest,
    NtdResponse,
    InfiniGramInfgramProbRequest,
    InfgramProbResponse,
    InfiniGramInfgramNtdRequest,
    InfgramNtdResponse,
)
from src.infinigram.infini_gram_dependency import InfiniGramProcessorDependency

infinigram_router = APIRouter()


@infinigram_router.get(path="/indexes")
def get_available_indexes() -> list[AvailableInfiniGramIndexId]:
    return [index for index in AvailableInfiniGramIndexId]


@infinigram_router.post(path="/{index}/find")
def find(
    infini_gram_processor: InfiniGramProcessorDependency,
    body: InfiniGramFindRequest,
) -> FindResponse:
    return infini_gram_processor.find(
        query=body.query,
    )


@infinigram_router.post(path="/{index}/find_cnf")
def find_cnf(
    infini_gram_processor: InfiniGramProcessorDependency,
    body: InfiniGramFindCnfRequest,
) -> FindCnfResponse:
    return infini_gram_processor.find_cnf(
        query=body.query,
        max_clause_freq=body.max_clause_freq,
        max_diff_tokens=body.max_diff_tokens,
    )


@infinigram_router.post(path="/{index}/count")
def count(
    infini_gram_processor: InfiniGramProcessorDependency,
    body: InfiniGramCountRequest,
) -> CountResponse:
    return infini_gram_processor.count(query=body.query)


@infinigram_router.post(path="/{index}/count_cnf")
def count_cnf(
    infini_gram_processor: InfiniGramProcessorDependency,
    body: InfiniGramCountCnfRequest,
) -> CountCnfResponse:
    return infini_gram_processor.count_cnf(
        query=body.query,
        max_clause_freq=body.max_clause_freq,
        max_diff_tokens=body.max_diff_tokens,
    )


@infinigram_router.post(path="/{index}/prob")
def prob(
    infini_gram_processor: InfiniGramProcessorDependency,
    body: InfiniGramProbRequest,
) -> ProbResponse:
    return infini_gram_processor.prob(
        query=body.query,
    )


@infinigram_router.post(path="/{index}/ntd")
def ntd(
    infini_gram_processor: InfiniGramProcessorDependency,
    body: InfiniGramNtdRequest,
) -> NtdResponse:
    return infini_gram_processor.ntd(
        query=body.query,
        max_support=body.max_support,
    )


@infinigram_router.post(path="/{index}/infgram_prob")
def infgram_prob(
    infini_gram_processor: InfiniGramProcessorDependency,
    body: InfiniGramInfgramProbRequest,
) -> InfgramProbResponse:
    return infini_gram_processor.infgram_prob(
        query=body.query,
    )


@infinigram_router.post(path="/{index}/infgram_ntd")
def infgram_ntd(
    infini_gram_processor: InfiniGramProcessorDependency,
    body: InfiniGramInfgramNtdRequest,
) -> InfgramNtdResponse:
    return infini_gram_processor.infgram_ntd(
        query=body.query,
        max_support=body.max_support,
    )
