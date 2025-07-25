from functools import lru_cache
from typing import Optional

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
def get_tokenizer_by_name(tokenizer_name: str) -> Tokenizer:
    """
    Get a tokenizer by name. Supports multiple tokenizer types.
    Falls back to llama-2 if tokenizer_name is not recognized.
    """
    config = get_processor_config()
    
    if tokenizer_name == "llama-2":
        return get_llama_2_tokenizer()
    elif tokenizer_name == "llama-3":
        return Tokenizer(
            pretrained_model_name_or_path=f"{config.vendor_base_path}/llama-3-8b-hf",
            delimiter_mapping={"\n": 13, ".": 29889},
            bow_ids_path=f"{config.vendor_base_path}/llama-3_bow_ids.txt",
        )
    # Add more tokenizers as needed
    # elif tokenizer_name == "gpt-4":
    #     return Tokenizer(...)
    else:
        # Default fallback to llama-2
        return get_llama_2_tokenizer()


def get_tokenizer_for_index(index_name: str) -> Tokenizer:
    """
    Get the appropriate tokenizer for a given index.
    This can be extended to have per-index tokenizer mappings.
    """
    # For now, use a simple mapping. This could be moved to config later.
    tokenizer_mappings = {
        "pileval-llama": "llama-2",
        "olmoe-0125-1b-7b": "llama-2",
        "olmo-2-1124-13b": "llama-2",
        "olmo-2-0325-32b": "llama-2",
        "tulu-3-8b": "llama-2",
        "tulu-3-70b": "llama-2", 
        "tulu-3-405b": "llama-2",
        # New indexes can specify different tokenizers
        # "new-gpt4-index": "gpt-4",
    }
    
    tokenizer_name = tokenizer_mappings.get(index_name, "llama-2")
    return get_tokenizer_by_name(tokenizer_name)
