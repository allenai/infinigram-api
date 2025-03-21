from itertools import islice
from typing import Iterable, Sequence

from infini_gram_processor.processor import InfiniGramProcessor


def get_span_text(
    infini_gram_index: InfiniGramProcessor,
    input_token_ids: Iterable[int],
    start: int,
    stop: int,
) -> tuple[Sequence[int], str]:
    span_text_tokens = list(islice(input_token_ids, start, stop))
    span_text = infini_gram_index.decode_tokens(token_ids=span_text_tokens)

    return (span_text_tokens, span_text)
