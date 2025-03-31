from fastapi_problem.error import Problem
from fastapi_problem.handler import ExceptionHandler
from infini_gram_processor.infini_gram_engine_exception import InfiniGramEngineException
from rfc9457 import error_class_to_type
from starlette.requests import Request


def infini_gram_engine_exception_handler(
    handler: ExceptionHandler, request: Request, exception: InfiniGramEngineException
) -> Problem:
    return Problem(
        title="infini-gram error",
        status=500,
        detail=exception.detail,
        type=error_class_to_type(exception),
    )
