from src.camel_case_model import CamelCaseModel


class RFC9457Error(CamelCaseModel):
    type: str = "about:blank"  # a URL pointing to a problem type definition
    title: str
    status: int
    detail: str
    instance: str
