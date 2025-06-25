from typing import Annotated
from infini_gram_processor.tokenizers.tokenizer_factory import get_llama_2_tokenizer
import os
from fastapi import Depends
from infini_gram_processor import indexes
from infini_gram_processor.index_mappings import AvailableInfiniGramIndexId
from infini_gram_processor.processor import InfiniGramProcessor


# def InfiniGramProcessorFactoryPathParam(
#     index: AvailableInfiniGramIndexId,
# ) -> InfiniGramProcessor:
#     return indexes[index]

    # Create a dynamic index configuration
def InfiniGramProcessorFactoryPathParam(index: str) -> InfiniGramProcessor:
    index_config = {
        "tokenizer": get_llama_2_tokenizer(),
        "index_dir": f"{os.getenv('INDEX_BASE_PATH', '/mnt/infinigram-array')}/{index}",
        "index_dir_diff": [],
    }
    
    processor = InfiniGramProcessor(index_config)
    return processor

InfiniGramProcessorDependency = Annotated[
    InfiniGramProcessor, Depends(InfiniGramProcessorFactoryPathParam)
]
