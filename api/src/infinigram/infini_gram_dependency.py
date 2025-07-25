from typing import Annotated
from infini_gram_processor.tokenizers.tokenizer_factory import get_llama_2_tokenizer, get_tokenizer_for_index
import os
from fastapi import Depends
from infini_gram_processor import indexes
from infini_gram_processor.index_mappings import AvailableInfiniGramIndexId
from infini_gram_processor.processor import InfiniGramProcessor

# Cache for dynamically created processors
_processor_cache: dict[str, InfiniGramProcessor] = {}

# def InfiniGramProcessorFactoryPathParam(
#     index: AvailableInfiniGramIndexId,
# ) -> InfiniGramProcessor:
#     return indexes[index]

def InfiniGramProcessorFactoryPathParam(index: str) -> InfiniGramProcessor:
    if index in _processor_cache:
        return _processor_cache[index]
    
    # dynamic index configuration with appropriate tokenizer
    index_config = {
        "tokenizer": get_tokenizer_for_index(index),
        "index_dir": f"{os.getenv('INDEX_BASE_PATH', '/mnt/infinigram-array')}/{index}",
        "index_dir_diff": [],
    }
    
    # Create and cache the processor
    processor = InfiniGramProcessor(index_config)
    _processor_cache[index] = processor
    return processor

InfiniGramProcessorDependency = Annotated[
    InfiniGramProcessor, Depends(InfiniGramProcessorFactoryPathParam)
]
