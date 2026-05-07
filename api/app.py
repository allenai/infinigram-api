import logging
import os

from fastapi import FastAPI
from fastapi_problem.handler import add_exception_handler
from infini_gram_processor.infini_gram_engine_exception import InfiniGramEngineException
from infinigram_api_shared.otel.otel_setup import set_up_tracing
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.logging import LoggingInstrumentor
from src import glog
from src.attribution import attribution_router
from src.config import get_config
from src.health import health_router
from src.infini_gram_exception_handler import infini_gram_engine_exception_handler
from src.infinigram import infinigram_router

LoggingInstrumentor().instrument()

# If LOG_FORMAT is "google:json" emit log message as JSON in a format Google Cloud can parse.
fmt = os.getenv("LOG_FORMAT")
handlers = [glog.create_stream_handler()] if fmt == "google:json" else []
level = os.environ.get("LOG_LEVEL", default=logging.INFO)
logging.basicConfig(level=level, handlers=handlers)


app = FastAPI(title="infini-gram API", version="0.0.1")
add_exception_handler(
    app,
    handlers={InfiniGramEngineException: infini_gram_engine_exception_handler},  # type: ignore
)

app.include_router(health_router)
app.include_router(router=infinigram_router)
app.include_router(router=attribution_router)

config = get_config()

set_up_tracing(
    is_otel_enabled=config.is_otel_enabled,
    is_prod_environment=config.is_prod_environment,
    otel_service_name=config.otel_service_name,
    env=config.skiff_env,
)

FastAPIInstrumentor.instrument_app(app, excluded_urls="health")
