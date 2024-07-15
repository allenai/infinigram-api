from pydantic import BaseModel


class RFC9457Error(BaseModel):
    type: str = "about:blank"  # a URL pointing to a problem type definition
    title: str
    status: int
    detail: str
    instance: str
