import sys
import traceback

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from src.infinigram.processor import InfiniGramQueryResponse, processor

infinigram_router = APIRouter()


class InfiniGramQuery(BaseModel):
    query: str


@infinigram_router.post("/query")
def query(body: InfiniGramQuery) -> InfiniGramQueryResponse:
    try:
        result = processor.find_docs_with_query(query=body.query)

        return result
    except Exception as e:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        traceback.print_exception(exc_type, exc_value, exc_traceback)

        raise HTTPException(
            status_code=500, detail=f"[FastAPI] Internal server error: {e}"
        )
