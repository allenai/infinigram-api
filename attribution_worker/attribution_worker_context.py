from infini_gram_processor.processor import InfiniGramProcessor
from saq.types import Context


class AttributionWorkerContext(Context):
    infini_gram_processor: InfiniGramProcessor
