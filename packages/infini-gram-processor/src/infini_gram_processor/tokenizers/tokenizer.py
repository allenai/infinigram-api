from os import PathLike
from typing import Iterable, List, Sequence, Tuple, cast

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
    bow_ids_path: str

    def __init__(
        self,
        pretrained_model_name_or_path: str | PathLike[str],
        bow_ids_path: str,
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
        self.bow_ids_path = bow_ids_path

    def tokenize(
        self, input: TextInput | PreTokenizedInput | EncodedInput
    ) -> List[int]:
        encoded_query: List[int] = self.hf_tokenizer.encode(input)  # pyright: ignore[reportUnknownMemberType]
        return encoded_query

    def decode_tokens(self, token_ids: Iterable[int]) -> str:
        return self.hf_tokenizer.decode(token_ids)  # type: ignore

    def tokenize_to_list(self, input: TextInput) -> Sequence[str]:
        tokenized_input = self.hf_tokenizer(input, return_offsets_mapping=True)

        offset_mapping = tokenized_input.data.get("offset_mapping", [])  # pyright: ignore [reportUnknownMemberType]
        # This is to fix a corner case: when input begins with a number, the token ids will begin with [29871 (whitespace), 29896, ...] with offset_mapping being [(0, 1), (0, 1), ...]
        if len(offset_mapping) > 1:
            if offset_mapping[0][1] > offset_mapping[1][0]:
                offset_mapping[0] = (offset_mapping[0][0], offset_mapping[1][0])

        return [
            input[offset[0] : offset[1]]
            for offset in cast(List[Tuple[(int, int)]], offset_mapping)
        ]

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
