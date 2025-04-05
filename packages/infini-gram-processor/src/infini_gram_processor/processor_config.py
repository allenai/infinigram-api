from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class ProcessorConfig(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    index_base_path: str = "/mnt/infinigram-array"
    vendor_base_path: str = "/app/vendor"


<<<<<<< Updated upstream
tokenizer_config = ProcessorConfig()


def get_processor_config() -> ProcessorConfig:
    return ProcessorConfig()
||||||| Stash base
tokenizer_config = TokenizerConfig()
=======
@lru_cache
def get_tokenizer_config() -> TokenizerConfig:
    return TokenizerConfig()
>>>>>>> Stashed changes
