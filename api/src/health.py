from fastapi import APIRouter, status

from src.infinigram.infini_gram_engine_exception import InfiniGramEngineException

health_router = APIRouter(prefix="/health")


# This tells the machinery that powers Skiff (Kubernetes) that your application
# is ready to receive traffic. Returning a non 2XX response code will prevent the
# application from receiving live requests.
@health_router.get("/", status_code=status.HTTP_204_NO_CONTENT)
async def health() -> None:
    raise InfiniGramEngineException("foo")
    return
