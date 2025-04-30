from fastapi import APIRouter
from infini_gram_processor.index_mappings import AvailableInfiniGramIndexId
from infini_gram_processor.models import (
    InfiniGramFindRequest,
    InfiniGramFindResponse,
    InfiniGramFindCnfRequest,
    InfiniGramFindCnfResponse,
    InfiniGramCountRequest,
    InfiniGramCountResponse,
    InfiniGramCountCnfRequest,
    InfiniGramProbRequest,
    InfiniGramProbResponse,
    InfiniGramNtdRequest,
    InfiniGramNtdResponse,
    InfiniGramInfgramProbRequest,
    InfiniGramInfgramProbResponse,
    InfiniGramInfgramNtdRequest,
    InfiniGramInfgramNtdResponse,
)
from src.camel_case_model import CamelCaseModel
from src.infinigram.infini_gram_dependency import InfiniGramProcessorDependency
from typing import List, Optional

infinigram_router = APIRouter()


@infinigram_router.get(path="/indexes")
def get_available_indexes() -> list[AvailableInfiniGramIndexId]:
    return [index for index in AvailableInfiniGramIndexId]


@infinigram_router.post(path="/{index}/find")
def find(
    infini_gram_processor: InfiniGramProcessorDependency,
    body: InfiniGramFindRequest,
) -> InfiniGramFindResponse:
    return infini_gram_processor.find(
        input_ids=body.input_ids,
    )


@infinigram_router.post(path="/{index}/find_cnf")
def find_cnf(
    infini_gram_processor: InfiniGramProcessorDependency,
    body: InfiniGramFindCnfRequest,
) -> InfiniGramFindCnfResponse:
    return infini_gram_processor.find_cnf(
        cnf=body.cnf,
        max_clause_freq=body.max_clause_freq,
        max_diff_tokens=body.max_diff_tokens,
    )


@infinigram_router.post(path="/{index}/count")
def count(
    infini_gram_processor: InfiniGramProcessorDependency,
    body: InfiniGramCountRequest,
) -> InfiniGramCountResponse:
    return infini_gram_processor.count(input_ids=body.input_ids)


@infinigram_router.post(path="/{index}/count_cnf")
def count_cnf(
    infini_gram_processor: InfiniGramProcessorDependency,
    body: InfiniGramCountCnfRequest,
) -> InfiniGramCountResponse:
    return infini_gram_processor.count_cnf(
        cnf=body.cnf,
        max_clause_freq=body.max_clause_freq,
        max_diff_tokens=body.max_diff_tokens,
    )


@infinigram_router.post(path="/{index}/prob")
def prob(
    infini_gram_processor: InfiniGramProcessorDependency,
    body: InfiniGramProbRequest,
) -> InfiniGramProbResponse:
    return infini_gram_processor.prob(
        prompt_ids=body.prompt_ids,
        cont_id=body.cont_id,
    )


@infinigram_router.post(path="/{index}/ntd")
def ntd(
    infini_gram_processor: InfiniGramProcessorDependency,
    body: InfiniGramNtdRequest,
) -> InfiniGramNtdResponse:
    return infini_gram_processor.ntd(
        prompt_ids=body.prompt_ids,
        max_support=body.max_support,
    )


@infinigram_router.post(path="/{index}/infgram_prob")
def infgram_prob(
    infini_gram_processor: InfiniGramProcessorDependency,
    body: InfiniGramInfgramProbRequest,
) -> InfiniGramInfgramProbResponse:
    return infini_gram_processor.infgram_prob(
        prompt_ids=body.prompt_ids,
        cont_id=body.cont_id,
    )


@infinigram_router.post(path="/{index}/infgram_ntd")
def infgram_ntd(
    infini_gram_processor: InfiniGramProcessorDependency,
    body: InfiniGramInfgramNtdRequest,
) -> InfiniGramInfgramNtdResponse:
    return infini_gram_processor.infgram_ntd(
        prompt_ids=body.prompt_ids,
        max_support=body.max_support,
    )
