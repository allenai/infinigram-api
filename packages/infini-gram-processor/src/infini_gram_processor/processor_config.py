from pydantic_settings import BaseSettings, SettingsConfigDict


class TokenizerConfig(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    index_base_path: str = "/mnt/infinigram-array"


tokenizer_config = TokenizerConfig()
