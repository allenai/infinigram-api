from os import PathLike
from typing import Iterable, List, Sequence

from transformers import (  # type: ignore
    AutoTokenizer,
    PreTrainedTokenizer,
    PreTrainedTokenizerFast,
)
from transformers.tokenization_utils_base import (  # type: ignore
    EncodedInput,
    PreTokenizedInput,
    TextInput,
)


class Tokenizer:
    hf_tokenizer: PreTrainedTokenizer | PreTrainedTokenizerFast
    delimiter_mapping: dict[str, int]
    eos_token_id: int

    def __init__(
        self,
        pretrained_model_name_or_path: str | PathLike[str],
        delimiter_mapping: dict[str, int] = {},
    ):
        self.hf_tokenizer = AutoTokenizer.from_pretrained(  # pyright: ignore[reportUnknownMemberType]
            pretrained_model_name_or_path=pretrained_model_name_or_path,
            add_bos_token=False,
            add_eos_token=False,
            trust_remote_code=True,
        )

        if self.hf_tokenizer.eos_token_id is None:
            raise Exception(
                f"The tokenizer for {pretrained_model_name_or_path} didn't have an eos token id"
            )

        self.eos_token_id = self.hf_tokenizer.eos_token_id
        self.delimiter_mapping = delimiter_mapping

    def tokenize(
        self, input: TextInput | PreTokenizedInput | EncodedInput
    ) -> List[int]:
        encoded_query: List[int] = self.hf_tokenizer.encode(input)  # pyright: ignore[reportUnknownMemberType]
        return encoded_query

    def decode_tokens(self, token_ids: Iterable[int]) -> str:
        return self.hf_tokenizer.decode(token_ids)  # pyright: ignore [reportUnknownMemberType]

    def decode_tokens_to_list(self, token_ids: List[int]) -> Sequence[str]:
        return self.hf_tokenizer.convert_ids_to_tokens(token_ids)

    def tokenize_attribution_delimiters(self, delimiters: Iterable[str]) -> List[int]:
        """
        A method made specifically to tokenize delimiters for attribution uses.

        The standard tokenization process gives us different results than we want for things like '.' and newlines. This function checks a pre-defined dict of strings to token IDs that provide the correct token for those delimiters.
        """
        encoded_delimiters: List[int] = []

        non_mapped_delimiters: List[str] = []

        for delimiter in delimiters:
            mapped_delimiter = self.delimiter_mapping.get(delimiter)

            if mapped_delimiter is not None:
                encoded_delimiters.append(mapped_delimiter)
            else:
                non_mapped_delimiters.append(delimiter)

        encoded_delimiters += (
            self.hf_tokenizer.encode(non_mapped_delimiters)  # pyright: ignore[reportUnknownMemberType]
            if len(non_mapped_delimiters) > 0
            else []
        )

        return encoded_delimiters
