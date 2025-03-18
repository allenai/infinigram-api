import asyncio
from enum import Enum
from typing import (
    Any,
    Iterable,
    List,
    Sequence,
    TypeGuard,
    TypeVar,
    cast,
)

from infini_gram.engine import InfiniGramEngineDiff
from infini_gram.models import (
    AttributionSpan,
    ErrorResponse,
    InfiniGramEngineResponse,
)
from pydantic import (
    BaseModel,
)
from saq import Queue
from saq.types import SettingsDict
from transformers.tokenization_utils_base import (  # type: ignore
    EncodedInput,
    PreTokenizedInput,
    TextInput,
)

from src.config import get_config
from src.index_mappings import AvailableInfiniGramIndexId, index_mappings
from src.infini_gram_engine_exception import InfiniGramEngineException

from .tokenizers.tokenizer import Tokenizer


class SpanRankingMethod(Enum):
    LENGTH = "length"
    UNIGRAM_LOGPROB_SUM = "unigram_logprob_sum"


class BaseInfiniGramResponse(BaseModel):
    index: str


class InfiniGramAttributionResponse(BaseInfiniGramResponse):
    spans: List[AttributionSpan]
    input_token_ids: List[int]


TInfiniGramResponse = TypeVar("TInfiniGramResponse")


def is_infini_gram_error_response(
    val: InfiniGramEngineResponse[TInfiniGramResponse],
) -> TypeGuard[ErrorResponse]:
    return isinstance(val, dict) and "error" in val


class InfiniGramProcessor:
    index: str
    tokenizer: Tokenizer
    infini_gram_engine: InfiniGramEngineDiff

    def __init__(self, index: AvailableInfiniGramIndexId):
        self.index = index.value
        index_mapping = index_mappings[index.value]

        self.tokenizer = index_mapping["tokenizer"]

        self.infini_gram_engine = InfiniGramEngineDiff(
            index_dir=index_mapping["index_dir"],
            index_dir_diff=index_mapping["index_dir_diff"],
            eos_token_id=self.tokenizer.eos_token_id,
            bow_ids_path=self.tokenizer.bow_ids_path,
            precompute_unigram_logprobs=True,
            # for the attribution feature, disabling prefetching can speed things up
            ds_prefetch_depth=0,
            sa_prefetch_depth=0,
            od_prefetch_depth=0,
        )

    def tokenize(
        self, input: TextInput | PreTokenizedInput | EncodedInput
    ) -> List[int]:
        return self.tokenizer.tokenize(input)

    def decode_tokens(self, token_ids: Iterable[int]) -> str:
        return self.tokenizer.decode_tokens(token_ids)

    def tokenize_to_list(self, input: TextInput) -> Sequence[str]:
        return self.tokenizer.tokenize_to_list(input)

    def __handle_error(
        self,
        result: InfiniGramEngineResponse[TInfiniGramResponse],
    ) -> TInfiniGramResponse:
        if is_infini_gram_error_response(result):
            raise InfiniGramEngineException(detail=result["error"])

        return cast(TInfiniGramResponse, result)

    # Attribute doesn't return a high-level response, it just returns stuff from the engine. Use this inside a service instead of returning it directly
    def attribute(
        self,
        input: str,
        delimiters: List[str],
        allow_spans_with_partial_words: bool,
        minimum_span_length: int,
        maximum_frequency: int,
    ) -> InfiniGramAttributionResponse:
        input_ids = self.tokenize(input)

        delimiter_token_ids = self.tokenizer.tokenize_attribution_delimiters(delimiters)

        attribute_response = self.infini_gram_engine.attribute(
            input_ids=input_ids,
            delim_ids=delimiter_token_ids,
            min_len=minimum_span_length,
            max_cnt=maximum_frequency,
            enforce_bow=not allow_spans_with_partial_words,
        )

        attribute_result = self.__handle_error(attribute_response)

        return InfiniGramAttributionResponse(
            **attribute_result,
            index=self.index,
            input_token_ids=input_ids,
        )


index = InfiniGramProcessor(AvailableInfiniGramIndexId.PILEVAL_LLAMA)


config = get_config()

queue = Queue.from_url(config.postgres_url, name="infini-gram-attribution")


async def start_worker():
    await queue.connect()


async def attribution_job(
    ctx: Any,
    *,
    input: str,
    delimiters: List[str],
    allow_spans_with_partial_words: bool,
    minimum_span_length: int,
    maximum_frequency: int,
):
    result = await asyncio.to_thread(
        index.attribute,
        input=input,
        delimiters=delimiters,
        allow_spans_with_partial_words=allow_spans_with_partial_words,
        minimum_span_length=minimum_span_length,
        maximum_frequency=maximum_frequency,
    )

    return result.model_dump_json()


settings = SettingsDict(
    queue=queue, functions=[("attribute", attribution_job)], concurrency=1
)
