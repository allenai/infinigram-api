from enum import Enum
from typing import Iterable, TypedDict

from src.config import config

from .tokenizers.tokenizer import Tokenizer
from .tokenizers.tokenizer_factory import get_llama_2_tokenizer


class AvailableInfiniGramIndexId(Enum):
    DOLMA_1_7 = "dolma-1_7"
    PILEVAL_LLAMA = "pileval-llama"
    OLMOE_MIX_0924 = "olmoe-mix-0924"
    OLMOE = "olmoe"


class IndexMapping(TypedDict):
    tokenizer: Tokenizer
    index_dir: str | Iterable[str]


IndexMappings = TypedDict(
    "IndexMappings",
    {
        "pileval-llama": IndexMapping,
        "dolma-1_7": IndexMapping,
        "olmoe-mix-0924": IndexMapping,
        "olmoe": IndexMapping,
    },
)

index_mappings: IndexMappings = {
    AvailableInfiniGramIndexId.PILEVAL_LLAMA.value: {
        "tokenizer": get_llama_2_tokenizer(),
        "index_dir": f"{config.index_base_path}/v4_pileval_llama",
    },
    AvailableInfiniGramIndexId.DOLMA_1_7.value: {
        "tokenizer": get_llama_2_tokenizer(),
        "index_dir": f"{config.index_base_path}/dolma_1_7",
    },
    AvailableInfiniGramIndexId.OLMOE_MIX_0924.value: {
        "tokenizer": get_llama_2_tokenizer(),
        "index_dir": [
            f"{config.index_base_path}/olmoe-mix-0924-dclm",
            f"{config.index_base_path}/olmoe-mix-0924-nodclm",
        ],
    },
    AvailableInfiniGramIndexId.OLMOE.value: {
        "tokenizer": get_llama_2_tokenizer(),
        "index_dir": [
            f"{config.index_base_path}/olmoe-mix-0924-dclm",
            f"{config.index_base_path}/olmoe-mix-0924-nodclm",
            f"{config.index_base_path}/v4-tulu-v3-1-mix",
            f"{config.index_base_path}/v4-ultrafeedback",
        ],
    },
}
