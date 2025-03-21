import logging
import os
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from infini_gram_processor.infini_gram_engine_exception import InfiniGramEngineException
from opentelemetry import trace
from opentelemetry.exporter.cloud_trace import CloudTraceSpanExporter
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, SimpleSpanProcessor
from src import glog
from src.attribution import attribution_router
from src.attribution.attribution_queue_service import (
    connect_to_attribution_queue,
    disconnect_from_attribution_queue,
)
from src.documents import documents_router
from src.health import health_router
from src.infinigram import infinigram_router
from src.RFC9457Error import RFC9457Error

# If LOG_FORMAT is "google:json" emit log message as JSON in a format Google Cloud can parse.
fmt = os.getenv("LOG_FORMAT")
handlers = [glog.create_stream_handler()] if fmt == "google:json" else []
level = os.environ.get("LOG_LEVEL", default=logging.INFO)
logging.basicConfig(level=level, handlers=handlers)


# https://fastapi.tiangolo.com/advanced/events/
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, Any]:
    # Things before yield on on startup
    await connect_to_attribution_queue()
    yield
    # Things after yield run on shutdown
    await disconnect_from_attribution_queue()


app = FastAPI(title="infini-gram API", version="0.0.1", lifespan=lifespan)

app.include_router(health_router)
app.include_router(router=infinigram_router)
app.include_router(router=documents_router)
app.include_router(router=attribution_router)


@app.exception_handler(InfiniGramEngineException)
def infini_gram_engine_exception_handler(
    request: Request, exception: InfiniGramEngineException
) -> JSONResponse:
    logger = logging.getLogger("uvicorn.error")

    logger.error(f"infini-gram engine exception: {exception}")

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


tracer_provider = TracerProvider()

if os.getenv("ENV") == "development":
    tracer_provider.add_span_processor(
        span_processor=SimpleSpanProcessor(OTLPSpanExporter())
    )
else:
    tracer_provider.add_span_processor(
        BatchSpanProcessor(CloudTraceSpanExporter(project_id="ai2-reviz"))  # type:ignore
    )

trace.set_tracer_provider(tracer_provider)

FastAPIInstrumentor.instrument_app(app, excluded_urls="health")
