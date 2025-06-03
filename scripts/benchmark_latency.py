import argparse
import json
import numpy as np
import requests
import time
from tqdm import tqdm

parser = argparse.ArgumentParser()
parser.add_argument('--input_path', type=str, required=True)
args = parser.parse_args()

api_url = 'http://0.0.0.0:8008/olmo-2-1124-13b/attribution'
params = {
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

with open(args.input_path) as f:
    ds = json.load(f)
# ds = ds[:5]

latencies_sec = []
lengths_tokens = []
for item in tqdm(ds):
    payload = {
        'prompt': item['prompt'],
        'response': item['response'],
        **params,
    }
    start_time = time.time()
    result = requests.post(api_url, json=payload).json()
    end_time = time.time()
    latency = end_time - start_time
    latencies_sec.append(latency)
    length_tokens = len(result['inputTokens'])
    lengths_tokens.append(length_tokens)

avg_latency_sec = np.mean(latencies_sec)
avg_length_tokens = np.mean(lengths_tokens)
print(f'Average latency: {avg_latency_sec:.2f} sec')
print(f'Average length: {avg_length_tokens:.2f} tokens')
print(f'All lengths: {list(sorted(lengths_tokens))}')
