from typing import TypedDict


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
    "pileval-llama": {
        "tokenizer": "./vendor/llama-2-7b-hf",
        "index_dir": "/mnt/infinigram-array/v4_pileval_llama",
    },
    "dolma-1_7": {
        "tokenizer": "./vendor/llama-2-7b-hf",
        "index_dir": "/mnt/infinigram-array/dolma_1_7",
    },
    "dolma-1_6-sample": {
        "tokenizer": "./vendor/olmo-7b",
        "index_dir": "/mnt/infinigram-array/dolma_1_7",
    },
}
