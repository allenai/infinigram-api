from enum import Enum
from typing import TypedDict


from .tokenizers.tokenizer import Tokenizer
from .tokenizers.tokenizer_factory import get_llama_2_tokenizer


class AvailableInfiniGramIndexId(Enum):
    DOLMA_1_7 = "dolma-1_7"
    # PILEVAL_LLAMA = "pileval-llama"


class IndexMapping(TypedDict):
    tokenizer: Tokenizer
    index_dir: str


IndexMappings = TypedDict(
    "IndexMappings",
    {
        "pileval-llama": IndexMapping,
        "dolma-1_7": IndexMapping,
    },
)

index_mappings: IndexMappings = {
    # AvailableInfiniGramIndexId.PILEVAL_LLAMA.value: {
    #     "tokenizer": get_llama_2_tokenizer(),
    #     "index_dir": f"{config.index_base_path}/v4_pileval_llama",
    # },
    AvailableInfiniGramIndexId.DOLMA_1_7.value: {
        "tokenizer": get_llama_2_tokenizer(),
        "index_dir": "/data-v4-dolma-v1_7-s0-llama/v4_dolma-v1_7-s0_llama",
    },
}
