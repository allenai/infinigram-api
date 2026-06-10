from pydantic_settings import BaseSettings, SettingsConfigDict


class ProcessorConfig(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    index_base_path: str = "/mnt/infinigram-array"
    vendor_base_path: str = "/app/vendor"

    MAX_QUERY_CHARS = 1000
    MAX_QUERY_TOKENS = 500
    MAX_CLAUSES_PER_CNF = 4
    MAX_TERMS_PER_CLAUSE = 4
    MAX_SUPPORT = 10000
    MAX_CLAUSE_FREQ = 500000
    MAX_DIFF_TOKENS = 1000


tokenizer_config = ProcessorConfig()


def get_processor_config() -> ProcessorConfig:
    return ProcessorConfig()
