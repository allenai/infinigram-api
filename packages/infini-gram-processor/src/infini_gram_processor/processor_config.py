from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class TokenizerConfig(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    index_base_path: str = "/mnt/infinigram-array"


@lru_cache
def get_tokenizer_config() -> TokenizerConfig:
    return TokenizerConfig()
