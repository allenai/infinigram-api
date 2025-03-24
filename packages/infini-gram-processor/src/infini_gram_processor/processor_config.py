from pydantic_settings import BaseSettings, SettingsConfigDict


class ProcessorConfig(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    index_base_path: str = "/mnt/infinigram-array"
    vendor_base_path: str = "/app/vendor"


tokenizer_config = ProcessorConfig()


def get_processor_config() -> ProcessorConfig:
    return ProcessorConfig()
