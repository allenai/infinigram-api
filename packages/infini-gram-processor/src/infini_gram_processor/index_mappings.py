from enum import Enum
from typing import Iterable, Literal, TypedDict

from .processor_config import tokenizer_config
from .tokenizers.tokenizer import Tokenizer
from .tokenizers.tokenizer_factory import get_dolma_2_tokenizer


class AvailableInfiniGramIndexId(Enum):
    OLMO_3_0625_7B_THINK = "olmo-3-0625-7b-think"
    # OLMO_3_0625_7B_INSTRUCT = "olmo-3-0625-7b-instruct"
    # OLMO_3_0625_32B_THINK = "olmo-3-0625-32b-think"


class IndexMapping(TypedDict):
    tokenizer: Tokenizer
    index_dir: str | Iterable[str]
    index_dir_diff: str | Iterable[str]
    token_dtype: Literal["u32"] | Literal["u16"]


# Python doesn't support exhaustive checking like TS does so we have to manually do this
# https://stackoverflow.com/questions/72022403/type-hint-for-an-exhaustive-dictionary-with-enum-literal-keys
IndexMappings = TypedDict(
    "IndexMappings",
    {
        "olmo-3-0625-7b-think": IndexMapping,
        # "olmo-3-0625-7b-instruct": IndexMapping,
        # "olmo-3-0625-32b-think": IndexMapping,
    },
)

index_mappings: IndexMappings = {
    AvailableInfiniGramIndexId.OLMO_3_0625_7B_THINK.value: {
        "tokenizer": get_dolma_2_tokenizer(),
        "index_dir": [
            f"{tokenizer_config.index_base_path}/dolma2-0625-base-shared",
            f"{tokenizer_config.index_base_path}/dolma2-0625-v01-7b",
        ],
        "index_dir_diff": [],
        "token_dtype": "u32",
    },
    # AvailableInfiniGramIndexId.OLMO_3_0625_7B_INSTRUCT.value: {
    #     "tokenizer": get_dolma_2_tokenizer(),
    #     "index_dir": [
    #         f"{tokenizer_config.index_base_path}/dolma2-0625-base-shared",
    #         f"{tokenizer_config.index_base_path}/dolma2-0625-v01-7b",
    #     ],
    #     "index_dir_diff": [],
    #     "token_dtype": "u32",
    # },
    # AvailableInfiniGramIndexId.OLMO_3_0625_32B_THINK.value: {
    #     "tokenizer": get_dolma_2_tokenizer(),
    #     "index_dir": [
    #         f"{tokenizer_config.index_base_path}/dolma2-0625-base-shared",
    #     ],
    #     "index_dir_diff": [],
    #     "token_dtype": "u32",
    # },
}
