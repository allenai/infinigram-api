from functools import lru_cache

from .tokenizer import Tokenizer


@lru_cache
def get_llama_2_tokenizer() -> Tokenizer:
    return Tokenizer(
        pretrained_model_name_or_path="./vendor/llama-2-7b-hf",
        delimiter_mapping={"\n": 13, ".": 29889},
        bow_ids_path="./vendor/llama-2_bow_ids.txt",
    )
