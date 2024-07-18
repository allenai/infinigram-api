from enum import Enum
from typing import TypedDict

from src.config import config


class AvailableInfiniGramIndexId(Enum):
    PILEVAL_LLAMA = "pileval-llama"
    DOLMA_1_7 = "dolma-1_7"
    DOLMA_1_6_SAMPLE = "dolma-1_6-sample"


class IndexMapping(TypedDict):
    tokenizer: str
    index_dir: str


IndexMappings = TypedDict(
    "IndexMappings",
    {
        "pileval-llama": IndexMapping,
        "dolma-1_7": IndexMapping,
        "dolma-1_6-sample": IndexMapping,
    },
)

index_mappings: IndexMappings = {
    AvailableInfiniGramIndexId.PILEVAL_LLAMA.value: {
        "tokenizer": "./vendor/llama-2-7b-hf",
        "index_dir": f"{config.index_base_path}/v4_pileval_llama",
    },
    AvailableInfiniGramIndexId.DOLMA_1_7.value: {
        "tokenizer": "./vendor/llama-2-7b-hf",
        "index_dir": f"{config.index_base_path}/dolma_1_7",
    },
    AvailableInfiniGramIndexId.DOLMA_1_6_SAMPLE.value: {
        "tokenizer": "./vendor/olmo-7b-hf",
        "index_dir": f"{config.index_base_path}/dolma_1_6_sample",
    },
}
