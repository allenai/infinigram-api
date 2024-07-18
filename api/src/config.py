from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    index_base_path: str = "/mnt/infinigram-array"


config = Config()


def get_config() -> Config:
    return config
