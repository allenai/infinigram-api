<<<<<<< Updated upstream
from pydantic import computed_field
||||||| Stash base
=======
from functools import lru_cache

>>>>>>> Stashed changes
from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    index_base_path: str = "/mnt/infinigram-array"
    profiling_enabled: bool = False
    application_name: str = "infini-gram-api"
<<<<<<< Updated upstream
    attribution_queue_url: str = "redis://localhost:6379"
    python_env: str = "prod"

    @computed_field  # type: ignore[prop-decorator]
    @property
    def attribution_queue_name(self) -> str:
        queue_prefix = "infini-gram-attribution"

        return f"{queue_prefix}-{self.python_env}"


config = Config()
||||||| Stash base
    attribution_queue_url: str = "redis://localhost:6379"


config = Config()
=======
    attribution_queue_url: str = "postgres://localhost:5432"
>>>>>>> Stashed changes


@lru_cache
def get_config() -> Config:
    return Config()
