from functools import lru_cache

from infini_gram_processor.processor_config import get_processor_config

from .tokenizer import Tokenizer


@lru_cache
def get_llama_2_tokenizer() -> Tokenizer:
    config = get_processor_config()
    return Tokenizer(
        pretrained_model_name_or_path=f"{config.vendor_base_path}/llama-2-7b-hf",
        delimiter_mapping={"\n": 13, ".": 29889},
        bow_ids_path=f"{config.vendor_base_path}/llama-2_bow_ids.txt",
    )


@lru_cache
def get_dolma_2_tokenizer() -> Tokenizer:
    config = get_processor_config()

    return Tokenizer(
        pretrained_model_name_or_path=f"{config.vendor_base_path}/dolma2-hf",
        delimiter_mapping={"\n": 198, ".": 13},
        bow_ids_path=None,
    )
