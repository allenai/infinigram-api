from enum import Enum
from typing import Callable, Iterable, Literal, TypedDict

from .processor_config import tokenizer_config
from .tokenizers.tokenizer import Tokenizer
from .tokenizers.tokenizer_factory import get_dolma_2_tokenizer, get_llama_2_tokenizer


class AvailableInfiniGramIndexId(Enum):
    # PILEVAL_LLAMA = "pileval-llama"
    # OLMOE_0125_1B_7B = "olmoe-0125-1b-7b"
    # OLMO_2_1124_13B = "olmo-2-1124-13b"
    OLMO_2_0325_32B = "olmo-2-0325-32b"
    # TULU_3_8B = "tulu-3-8b"
    # TULU_3_70B = "tulu-3-70b"
    # TULU_3_405B = "tulu-3-405b"
    OLMO_3_0625_7B_THINK = "olmo-3-0625-7b-think"
    OLMO_3_0625_7B_INSTRUCT = "olmo-3-0625-7b-instruct"
    OLMO_3_0625_32B_THINK = "olmo-3-0625-32b-think"
    # OLMO_3_0625_32B_INSTRUCT = "olmo-3-0625-32b-instruct"


class IndexMapping(TypedDict):
    tokenizer_factory: Callable[[], Tokenizer]
    index_dir: str | Iterable[str]
    index_dir_diff: str | Iterable[str]
    token_dtype: Literal["u32"] | Literal["u16"]


# Python doesn't support exhaustive checking like TS does so we have to manually do this
# https://stackoverflow.com/questions/72022403/type-hint-for-an-exhaustive-dictionary-with-enum-literal-keys
IndexMappings = TypedDict(
    "IndexMappings",
    {
        # "pileval-llama": IndexMapping,
        # "olmoe-0125-1b-7b": IndexMapping,
        # "olmo-2-1124-13b": IndexMapping,
        "olmo-2-0325-32b": IndexMapping,
        # "tulu-3-8b": IndexMapping,
        # "tulu-3-70b": IndexMapping,
        # "tulu-3-405b": IndexMapping,
        "olmo-3-0625-7b-think": IndexMapping,
        "olmo-3-0625-7b-instruct": IndexMapping,
        "olmo-3-0625-32b-think": IndexMapping,
        # "olmo-3-0625-32b-instruct": IndexMapping,
    },
)

index_mappings: IndexMappings = {
    # AvailableInfiniGramIndexId.PILEVAL_LLAMA.value: {
    #     "tokenizer_factory": get_llama_2_tokenizer,
    #     "index_dir": f"{tokenizer_config.index_base_path}/v4_pileval_llama",
    #     "index_dir_diff": [],
    #     "token_dtype": "u16",
    # },
    # AvailableInfiniGramIndexId.OLMOE_0125_1B_7B.value: {
    #     "tokenizer_factory": get_llama_2_tokenizer,
    #     "index_dir": [
    #         f"{tokenizer_config.index_base_path}/olmoe-mix-0924-dclm",
    #         f"{tokenizer_config.index_base_path}/olmoe-mix-0924-nodclm",
    #         f"{tokenizer_config.index_base_path}/v4-olmoe-0125-1b-7b-anneal-adapt",
    #     ],
    #     "index_dir_diff": [],
    #     "token_dtype": "u16",
    # },
    # AvailableInfiniGramIndexId.OLMO_2_1124_13B.value: {
    #     "tokenizer_factory": get_llama_2_tokenizer,
    #     "index_dir": [
    #         f"{tokenizer_config.index_base_path}/olmoe-mix-0924-dclm",
    #         f"{tokenizer_config.index_base_path}/olmoe-mix-0924-nodclm",
    #         f"{tokenizer_config.index_base_path}/v4-olmo-2-1124-13b-anneal-adapt",
    #     ],
    #     "index_dir_diff": [],
    #     "token_dtype": "u16",
    # },
    AvailableInfiniGramIndexId.OLMO_2_0325_32B.value: {
        "tokenizer_factory": get_llama_2_tokenizer,
        "index_dir": [
            f"{tokenizer_config.index_base_path}/olmoe-mix-0924-dclm",
            f"{tokenizer_config.index_base_path}/olmoe-mix-0924-nodclm",
            f"{tokenizer_config.index_base_path}/v4-olmo-2-0325-32b-anneal-adapt",
        ],
        "index_dir_diff": [],
        "token_dtype": "u16",
    },
    # AvailableInfiniGramIndexId.TULU_3_8B.value: {
    #     "tokenizer_factory": get_llama_2_tokenizer,
    #     "index_dir": [
    #         f"{tokenizer_config.index_base_path}/v4-tulu-3-8b-adapt",
    #     ],
    #     "index_dir_diff": [],
    #     "token_dtype": "u16",
    # },
    # AvailableInfiniGramIndexId.TULU_3_70B.value: {
    #     "tokenizer_factory": get_llama_2_tokenizer,
    #     "index_dir": [
    #         f"{tokenizer_config.index_base_path}/v4-tulu-3-70b-adapt",
    #     ],
    #     "index_dir_diff": [],
    #     "token_dtype": "u16",
    # },
    # AvailableInfiniGramIndexId.TULU_3_405B.value: {
    #     "tokenizer_factory": get_llama_2_tokenizer,
    #     "index_dir": [
    #         f"{tokenizer_config.index_base_path}/v4-tulu-3-405b-adapt",
    #     ],
    #     "index_dir_diff": [],
    #     "token_dtype": "u16",
    # },
    AvailableInfiniGramIndexId.OLMO_3_0625_7B_THINK.value: {
        "tokenizer_factory": get_dolma_2_tokenizer,
        "index_dir": [
            f"{tokenizer_config.index_base_path}/dolma2-0625-base-shared",
            f"{tokenizer_config.index_base_path}/dolma2-0625-v01-7b",
        ],
        "index_dir_diff": [],
        "token_dtype": "u32",
    },
    AvailableInfiniGramIndexId.OLMO_3_0625_7B_INSTRUCT.value: {
        "tokenizer_factory": get_dolma_2_tokenizer,
        "index_dir": [
            f"{tokenizer_config.index_base_path}/dolma2-0625-base-shared",
            f"{tokenizer_config.index_base_path}/dolma2-0625-v01-7b",
        ],
        "index_dir_diff": [],
        "token_dtype": "u32",
    },
    AvailableInfiniGramIndexId.OLMO_3_0625_32B_THINK.value: {
        "tokenizer_factory": get_dolma_2_tokenizer,
        "index_dir": [
            f"{tokenizer_config.index_base_path}/dolma2-0625-base-shared",
            f"{tokenizer_config.index_base_path}/v6-dolma2-0625-v02-32b",
        ],
        "index_dir_diff": [],
        "token_dtype": "u32",
    },
    # AvailableInfiniGramIndexId.OLMO_3_0625_32B_INSTRUCT.value: {
    #     "tokenizer_factory": get_dolma_2_tokenizer,
    #     "index_dir": [
    #         f"{tokenizer_config.index_base_path}/dolma2-0625-base-shared",
    #         f"{tokenizer_config.index_base_path}/v6-dolma2-0625-v02-32b",
    #     ],
    #     "index_dir_diff": [],
    #     "token_dtype": "u32",
    # },
}
