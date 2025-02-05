import requests
import multiprocessing as mp
import random

NUM_TOKENS = 200
NUM_CONCURRENT_REQUESTS = 3

PAYLOAD = {
    'prompt': '',
    'response': '',
    'delimiters': ['\n', '.'],
    'allowSpansWithPartialWords': False,
    'minimumSpanLength': 1,
    'maximumFrequency': 1000000,
    'maximumSpanDensity': 0.05,
    'spanRankingMethod': 'unigram_logprob_sum',
    'includeDocuments': True,
    'maximumDocumentsPerSpan': 10,
    'maximumDocumentContextLengthRetrieved': 250,
    'maximumDocumentContextLengthDisplayed': 50,
    'filterMethod': 'bm25',
    'filterBm25FieldsConsidered': 'prompt|response',
    'filterBm25RatioToKeep': 1.0,
    'includeInputAsTokens': True,
}

url = 'http://0.0.0.0:8008/olmo-2-1124-13b/attribution'
# url = 'https://infinigram-api.allen.ai/olmo-2-1124-13b/attribution'

def issue_request(response):
    payload = PAYLOAD.copy()
    payload['response'] = response
    return requests.post(url, json=payload).json()

with mp.get_context('fork').Pool(NUM_CONCURRENT_REQUESTS) as p:
    responses = []
    for i in range(NUM_CONCURRENT_REQUESTS):
        response = ''
        for j in range(NUM_TOKENS):
            response += str(random.randint(0, 9))
        responses.append(response)
    results = p.map(issue_request, responses)

    for i in range(NUM_CONCURRENT_REQUESTS):
        result = issue_request(responses[i])
        assert result == results[i]
