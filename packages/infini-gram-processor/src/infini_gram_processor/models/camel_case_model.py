from pydantic import BaseModel
from pydantic.alias_generators import to_camel


class CamelCaseConfigMixin:
    class Config:
        alias_generator = to_camel
        populate_by_name = True


class CamelCaseModel(BaseModel, CamelCaseConfigMixin): ...


class ApiRequest(BaseModel, CamelCaseConfigMixin, frozen=True): ...
