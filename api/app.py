import logging
import os

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from src import glog
from src.health import health_router
from src.infinigram import infinigram_router
from src.infinigram.infini_gram_engine_exception import InfiniGramEngineException
from src.RFC9457Error import RFC9457Error

# If LOG_FORMAT is "google:json" emit log message as JSON in a format Google Cloud can parse.
fmt = os.getenv("LOG_FORMAT")
handlers = [glog.Handler()] if fmt == "google:json" else []
level = os.environ.get("LOG_LEVEL", default=logging.INFO)
logging.basicConfig(level=level, handlers=handlers)

app = FastAPI()
app.include_router(health_router)
app.include_router(router=infinigram_router)


@app.exception_handler(InfiniGramEngineException)
def infini_gram_engine_exception_handler(
    request: Request, exception: InfiniGramEngineException
) -> JSONResponse:
    response = RFC9457Error(
        title="infini-gram error",
        status=500,
        detail=exception.detail,
        instance=f"{request.url}",
    )

    return JSONResponse(
        status_code=response.status,
        content=response.model_dump(),
    )
