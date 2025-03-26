from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    index_base_path: str = "/mnt/infinigram-array"
    application_name: str = "infini-gram-api"
    attribution_queue_url: str = "redis://localhost:6379"
    python_env: str = "prod"

    @computed_field  # type: ignore[prop-decorator]
    @property
    def attribution_queue_name(self) -> str:
        queue_prefix = "infini-gram-attribution"

        return f"{queue_prefix}-{self.python_env}"


config = Config()


def get_config() -> Config:
    return config
