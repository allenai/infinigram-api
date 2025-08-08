import json
import requests
from tqdm import tqdm

payload = {
    'response': None,
    'delimiters': ['\n', '.'],
    'allowSpansWithPartialWords': False,
    'minimumSpanLength': 1,
    'maximumFrequency': 1000000,
    'maximumSpanDensity': 0.05,
    'spanRankingMethod': 'unigram_logprob_sum',
    'maximumDocumentsPerSpan': 10,
    'maximumContextLength': 250,
    'maximumContextLengthLong': 250,
    'maximumContextLengthSnippet': 40,
}

url = 'https://infinigram-api.allen.ai/olmoe-0125-1b-7b/attribution'
# url = 'http://0.0.0.0:8008/tulu-3-405b/attribution'

with open('data/bailey100.json') as f:
    ds = json.load(f)

for item in tqdm(ds):
    payload['response'] = item['response']
    result = requests.post(url, json=payload).json()
    item['spans'] = result['spans']

with open('data/bailey100_newhparams.json', 'w') as f:
    json.dump(ds, f, indent=4)
