import argparse
import json
import numpy as np
import requests
from openai import OpenAI
import os
from tqdm import tqdm

client = OpenAI(
    api_key=os.environ['OPENAI_API_KEY'],
)

parser = argparse.ArgumentParser()
parser.add_argument('--input_path', type=str, required=True)
parser.add_argument('--output_path', type=str, required=True)
parser.add_argument('--overwrite_docs', default=False, action='store_true')
args = parser.parse_args()

api_url = 'https://infinigram-api.allen.ai/olmoe/attribution'
params = {
    'delimiters': ['\n', '.'],
    'allowSpansWithPartialWords': False,
    'minimumSpanLength': 1,
    'maximumFrequency': 1000000,
    'maximumSpanDensity': 0.05,
    'spanRankingMethod': 'unigram_logprob_sum',
    'includeDocuments': True,
    'maximumDocumentsPerSpan': 10,
    'maximumDocumentDisplayLength': 100,
    'filterMethod': 'bm25',
    'filterBm25FieldsConsidered': 'prompt|response',
    'filterBm25RatioToKeep': 1.0,
    'includeInputAsTokens': True,
}

with open(args.input_path) as f:
    ds = json.load(f)
# ds = ds[:10]

results = []

for item in tqdm(ds):

    if 'docs' not in item or args.overwrite_docs:
        payload = {
            'prompt': item['prompt'],
            'response': item['response'],
            **params,
        }
        result = requests.post(api_url, json=payload).json()

        doc_by_ix = {}
        for span in result['spans']:
            for doc in span['documents']:
                if doc['documentIndex'] not in doc_by_ix:
                    try:
                        url = doc['metadata']['metadata']['metadata']['url']
                    except:
                        url = None
                    doc_by_ix[doc['documentIndex']] = {
                        'documentIndex': doc['documentIndex'],
                        'url': url,
                        'relevanceScore': doc['relevanceScore'],
                        'spanTexts': [span['text']],
                        'snippets': [doc['text']],
                    }
                else:
                    doc_by_ix[doc['documentIndex']]['spanTexts'].append(span['text'])
                    doc_by_ix[doc['documentIndex']]['snippets'].append(doc['text'])
        docs = list(sorted(doc_by_ix.values(), key=lambda x: x['relevanceScore'], reverse=True))

        item['docs'] = docs

        max_doc_score = max(doc['relevanceScore'] for doc in item['docs'])
        min_doc_score = min(doc['relevanceScore'] for doc in item['docs'])
        max_span_score = max(max(doc['relevanceScore'] for doc in span['documents']) for span in result['spans'])
        min_span_score = min(max(doc['relevanceScore'] for doc in span['documents']) for span in result['spans'])
        response_len_chars = len(item['response'])
        results.append({
            'response_len_chars': response_len_chars,
            'max_doc_score': max_doc_score,
            'min_doc_score': min_doc_score,
            'max_span_score': max_span_score,
            'min_span_score': min_span_score,
        })

# Make a plot where the x-axis is the length of the response in characters, and the y-axis is a bar from min to max score of the documents.
import matplotlib.pyplot as plt
import seaborn as sns
sns.set(style='whitegrid')

plt.figure(figsize=(12, 8))
plt.scatter([r['response_len_chars'] for r in results], [r['max_doc_score'] for r in results], label='max doc score')
plt.scatter([r['response_len_chars'] for r in results], [r['min_doc_score'] for r in results], label='min doc score')
plt.xlabel('Response length (characters)')
plt.ylabel('Document score')
plt.legend()
plt.savefig('distrib_of_score_doc.png', dpi=300)

plt.figure(figsize=(12, 8))
plt.scatter([r['response_len_chars'] for r in results], [r['max_span_score'] for r in results], label='max span score')
plt.scatter([r['response_len_chars'] for r in results], [r['min_span_score'] for r in results], label='min span score')
plt.xlabel('Response length (characters)')
plt.ylabel('Span score')
plt.legend()
plt.savefig('distrib_of_score_span.png', dpi=300)

