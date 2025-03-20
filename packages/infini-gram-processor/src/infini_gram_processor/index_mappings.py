from enum import Enum
from typing import Iterable, TypedDict

from .tokenizers.tokenizer import Tokenizer
from .tokenizers.tokenizer_config import tokenizer_config
from .tokenizers.tokenizer_factory import get_llama_2_tokenizer


class AvailableInfiniGramIndexId(Enum):
    PILEVAL_LLAMA = "pileval-llama"
    OLMOE_0125_1B_7B = "olmoe-0125-1b-7b"
    OLMO_2_1124_13B = "olmo-2-1124-13b"
    OLMO_2_0325_32B = "olmo-2-0325-32b"


class IndexMapping(TypedDict):
    tokenizer: Tokenizer
    index_dir: str | Iterable[str]
    index_dir_diff: str | Iterable[str]


IndexMappings = TypedDict(
    "IndexMappings",
    {
        "pileval-llama": IndexMapping,
        "olmoe-0125-1b-7b": IndexMapping,
        "olmo-2-1124-13b": IndexMapping,
        "olmo-2-0325-32b": IndexMapping,
    },
)

index_mappings: IndexMappings = {
    AvailableInfiniGramIndexId.PILEVAL_LLAMA.value: {
        "tokenizer": get_llama_2_tokenizer(),
        "index_dir": f"{tokenizer_config.index_base_path}/v4_pileval_llama",
        "index_dir_diff": [],
    },
    AvailableInfiniGramIndexId.OLMOE_0125_1B_7B.value: {
        "tokenizer": get_llama_2_tokenizer(),
        "index_dir": [
            f"{tokenizer_config.index_base_path}/olmoe-mix-0924-dclm",
            f"{tokenizer_config.index_base_path}/olmoe-mix-0924-nodclm",
            f"{tokenizer_config.index_base_path}/v4-olmoe-0125-1b-7b-anneal-adapt",
        ],
        "index_dir_diff": [],
    },
    AvailableInfiniGramIndexId.OLMO_2_1124_13B.value: {
        "tokenizer": get_llama_2_tokenizer(),
        "index_dir": [
            f"{tokenizer_config.index_base_path}/olmoe-mix-0924-dclm",
            f"{tokenizer_config.index_base_path}/olmoe-mix-0924-nodclm",
            f"{tokenizer_config.index_base_path}/v4-olmo-2-1124-13b-anneal-adapt",
        ],
        "index_dir_diff": [],
    },
    AvailableInfiniGramIndexId.OLMO_2_0325_32B.value: {
        "tokenizer": get_llama_2_tokenizer(),
        "index_dir": [
            f"{tokenizer_config.index_base_path}/olmoe-mix-0924-dclm",
            f"{tokenizer_config.index_base_path}/olmoe-mix-0924-nodclm",
            f"{tokenizer_config.index_base_path}/v4-olmo-2-0325-32b-anneal-adapt",
        ],
        "index_dir_diff": [],
    },
}
