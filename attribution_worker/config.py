from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", extra="ignore", secrets_dir="/secret/env"
    )
    index_base_path: str = "/mnt/infinigram-array"
    application_name: str = "infini-gram-api-worker"
    attribution_queue_url: str = "redis://localhost:6379"
    skiff_env: str = "prod"

    is_otel_enabled: bool = True
    otel_service_name: str = "infinigram-api"

    @computed_field  # type: ignore[prop-decorator]
    @property
    def attribution_queue_name(self) -> str:
        queue_prefix = "infini-gram-attribution"

        return f"{queue_prefix}-{self.skiff_env}"

    @computed_field  # type: ignore[prop-decorator]
    @property
    def is_prod_environment(self) -> bool:
        return self.skiff_env == "prod"


config = Config()


def get_config() -> Config:
    return config
