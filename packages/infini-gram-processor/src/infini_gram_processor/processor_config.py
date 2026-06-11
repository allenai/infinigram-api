from pydantic_settings import BaseSettings, SettingsConfigDict


class ProcessorConfig(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    index_base_path: str = "/mnt/infinigram-array"
    vendor_base_path: str = "/app/vendor"

    max_query_chars: int = 1000
    max_query_tokens: int = 500
    max_clauses_per_cnf: int = 4
    max_terms_per_clause: int = 4
    max_support: int = 10000
    max_clause_freq: int = 500000
    max_diff_tokens: int = 1000


tokenizer_config = ProcessorConfig()


def get_processor_config() -> ProcessorConfig:
    return ProcessorConfig()
