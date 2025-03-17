from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    index_base_path: str = "/mnt/infinigram-array"
    profiling_enabled: bool = False
    application_name: str = "infini-gram-api"
    postgres_url: str = "postgres://postgres:llmz@127.0.0.1:5555/llmx?sslmode=disable&application_name=infini-gram-attribution-worker"


config = Config()


def get_config() -> Config:
    return config
