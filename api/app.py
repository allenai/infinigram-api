import logging
import os

from fastapi import FastAPI
from src import glog
from src.health import health_router

# If LOG_FORMAT is "google:json" emit log message as JSON in a format Google Cloud can parse.
fmt = os.getenv("LOG_FORMAT")
handlers = [glog.Handler()] if fmt == "google:json" else []
level = os.environ.get("LOG_LEVEL", default=logging.INFO)
logging.basicConfig(level=level, handlers=handlers)

app = FastAPI()
app.include_router(health_router)
# app.include_router(router=infinigram_router)
