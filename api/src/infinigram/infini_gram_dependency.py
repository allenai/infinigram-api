from typing import Annotated

from fastapi import Depends
from infini_gram_processor import get_indexes
from infini_gram_processor.index_mappings import AvailableInfiniGramIndexId
from infini_gram_processor.processor import InfiniGramProcessor


def InfiniGramProcessorFactoryPathParam(
    index: AvailableInfiniGramIndexId,
) -> InfiniGramProcessor:
    return get_indexes()[index]


InfiniGramProcessorDependency = Annotated[
    InfiniGramProcessor, Depends(InfiniGramProcessorFactoryPathParam)
]
