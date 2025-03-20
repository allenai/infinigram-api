from typing import TypeGuard, TypeVar

from infini_gram.models import (
    ErrorResponse,
    InfiniGramEngineResponse,
)

TInfiniGramResponse = TypeVar("TInfiniGramResponse")


def is_infini_gram_error_response(
    val: InfiniGramEngineResponse[TInfiniGramResponse],
) -> TypeGuard[ErrorResponse]:
    return isinstance(val, dict) and "error" in val
