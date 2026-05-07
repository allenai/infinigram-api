from functools import lru_cache
from typing import Annotated

from fastapi import Depends
from pydantic import Field, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    index_base_path: str = "/mnt/infinigram-array"
    profiling_enabled: bool = False
    application_name: str = "infini-gram-api"
    attribution_queue_url: str = Field(init=False)
    skiff_env: str = "prod"
    cache_url: str = Field(init=False)

    is_otel_enabled: bool = True
    otel_service_name: str = "infinigram-api"

    @computed_field  # type: ignore[prop-decorator]
    @property
    def attribution_queue_name(self) -> str:
        queue_prefix = "infini-gram-attribution"

        return f"{queue_prefix}-{self.skiff_env}"

    @computed_field
    @property
    def is_prod_environment(self) -> bool:
        return self.skiff_env == "prod"


@lru_cache
def get_config() -> Config:
    return Config()


ConfigDependency = Annotated[Config, Depends(get_config)]
