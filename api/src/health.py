from fastapi import APIRouter, status

health_router = APIRouter(prefix="/health")


# This tells the machinery that powers Skiff (Kubernetes) that your application
# is ready to receive traffic. Returning a non 2XX response code will prevent the
# application from receiving live requests.
@health_router.get("/", status_code=status.HTTP_204_NO_CONTENT)
def health() -> None:
    return
