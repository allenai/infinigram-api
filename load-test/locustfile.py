import json
import random
from dataclasses import dataclass
from typing import Callable

from infini_gram_processor.index_mappings import AvailableInfiniGramIndexId
from locust import HttpUser, run_single_user

with open("bailey100.json", "r") as file:
    bailey = json.load(file)


@dataclass
class AttributionData:
    prompt: str
    response: str


def create_task(data: AttributionData) -> Callable[..., None]:
    request = {
        "prompt": data.prompt,
        "response": data.response,
        "delimiters": ["\n", "."],
        "allowSpansWithPartialWords": True,
        "minimumSpanLength": 1,
        "maximumFrequency": 1000000,
        "maximumSpanDensity": 0.05,
        "spanRankingMethod": "unigram_logprob_sum",
        "includeDocuments": True,
        "maximumDocumentsPerSpan": 10,
        "maximum_document_context_length_retrieved": 250,
        "maximum_document_context_length_displayed": 40,
        "filterMethod": "bm25",
        "filterBm25FieldsConsidered": "prompt|response",
        "filterBm25RatioToKeep": 1.0,
        "includeInputAsTokens": True,
    }

    def get_attribution(self: "InfiniGramApiUser") -> None:
        index = random.choice([index.value for index in AvailableInfiniGramIndexId])
        self.client.post(f"/{index}/attribution", json=request)

    return get_attribution


class InfiniGramApiUser(HttpUser):
    tasks = [
        create_task(AttributionData(entry["prompt"], entry["response"]))
        for entry in bailey
    ]


if __name__ == "__main__":
    run_single_user(InfiniGramApiUser)
