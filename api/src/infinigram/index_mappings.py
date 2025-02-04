from enum import Enum
from typing import Iterable, TypedDict

from src.config import config

from .tokenizers.tokenizer import Tokenizer
from .tokenizers.tokenizer_factory import get_llama_2_tokenizer


class AvailableInfiniGramIndexId(Enum):
    PILEVAL_LLAMA = "pileval-llama"
    OLMO_2_1124_13B = "olmo-2-1124-13b"


class IndexMapping(TypedDict):
    tokenizer: Tokenizer
    index_dir: str | Iterable[str]


IndexMappings = TypedDict(
    "IndexMappings",
    {
        "pileval-llama": IndexMapping,
        "olmo-2-1124-13b": IndexMapping,
    },
)

index_mappings: IndexMappings = {
    AvailableInfiniGramIndexId.PILEVAL_LLAMA.value: {
        "tokenizer": get_llama_2_tokenizer(),
        "index_dir": f"{config.index_base_path}/v4_pileval_llama",
    },
    AvailableInfiniGramIndexId.OLMO_2_1124_13B.value: {
        "tokenizer": get_llama_2_tokenizer(),
        "index_dir": [
            f"{config.index_base_path}/olmoe-mix-0924-dclm",
            f"{config.index_base_path}/olmoe-mix-0924-nodclm",
            f"{config.index_base_path}/v4-olmo-2-1124-13b-anneal-adapt",
        ],
    },
}
