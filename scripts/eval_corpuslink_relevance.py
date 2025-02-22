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
parser.add_argument('--overwrite_eval', default=False, action='store_true')
parser.add_argument('--num_docs_per_thread', type=int, default=5)
args = parser.parse_args()

api_url = 'http://0.0.0.0:8008/olmoe/attribution'
params = {
    'delimiters': ['\n', '.'],
    'allowSpansWithPartialWords': False,
    'minimumSpanLength': 1,
    'maximumFrequency': 1000000,
    'maximumSpanDensity': 0.05,
    'spanRankingMethod': 'unigram_logprob_sum',
    'includeDocuments': True,
    'maximumDocumentsPerSpan': 10,
    'maximumDocumentDisplayLength': 500,
    'filterMethod': 'bm25',
    'filterBm25FieldsConsidered': 'prompt|response',
    'filterBm25RatioToKeep': 1.0,
    'includeInputAsTokens': True,
}

# llm_as_a_judge_system_message = """You will be given a user prompt, a model's response to the prompt, and a retrieved document. Please rate how relevant the document is to the prompt and model response. Rate on a scale of 0 (not relevant) to 3 (very relevant). Respond with a single number, and do not include any other text in your response."""
llm_as_a_judge_system_message = """You will be given a user prompt, a model's response to the prompt, and a retrieved document. Please rate how relevant the document is to the prompt and model response. Rate on a scale of 0 (not relevant) to 3 (very relevant). Respond with a single number, and do not include any other text in your response.

Rubric for rating:
0: The document is about a different topic than the prompt and model response.
1. The document is about a broader topic than the prompt and model response, or is potentially relevant but there's not enough information.
2. The document is on the right topic of the prompt and model response, but is in a slightly different context or is too specific.
3. The document is about a subject that is a direct match, in topic and scope, of the most likely user intent for the prompt and model response."""
llm_as_a_judge_template = """Prompt: {prompt}

Model response: {response}

Retrieved document: {document}"""
# llm_as_a_judge_system_message = """You will be given a user prompt, a model's response to the prompt, and a retrieved document. Please rate how relevant the document is to the prompt and model response. Rate on a scale of 0 (not relevant) to 3 (very relevant). Provide your reasoning first, and finally give your rating in the format of "Rating: X". Please strictly follow this template, and do not include any other text or character after the rating.

# Rubric for rating:
# 0: The document is about a different topic than the prompt and model response.
# 1. The document is about a broader topic than the prompt and model response, or is potentially relevant but there's not enough information.
# 2. The document is on the right topic of the prompt and model response, but is in a slightly different context or is too specific.
# 3. The document is about a subject that is a direct match, in topic and scope, of the most likely user intent for the prompt and model response."""
# llm_as_a_judge_template = """Prompt: {prompt}

# Model response: {response}

# Retrieved document: {document}"""
# llm_as_a_judge_system_message = """You will be given a user prompt, a model's response to the prompt, and a retrieved document. Please rate how relevant the document is to the prompt and model response. Rate on a scale of 0 (not relevant) to 3 (very relevant). First give your rating as a single number on its own line, and then provide your reasoning on this rating. Please strictly follow this format, and do not include any other text in the first line than the rating number.

# Rubric for rating:
# 0: The document is about a different topic than the prompt and model response.
# 1. The document is about a broader topic than the prompt and model response, or is potentially relevant but there's not enough information.
# 2. The document is on the right topic of the prompt and model response, but is in a slightly different context or is too specific.
# 3. The document is about a subject that is a direct match, in topic and scope, of the most likely user intent for the prompt and model response."""
# llm_as_a_judge_template = """Prompt: {prompt}

# Model response: {response}

# Retrieved document: {document}"""

with open(args.input_path) as f:
    ds = json.load(f)
# ds = ds[:5]

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

        deduped_docs = []
        for doc in docs:
            if doc['url'] is None or doc['url'] not in [d['url'] for d in deduped_docs]:
                deduped_docs.append(doc)
        docs = deduped_docs

        docs = docs[:args.num_docs_per_thread]

        item['docs'] = docs

    for doc in item['docs']:
        if 'rating' not in doc or args.overwrite_eval:
            user_message = llm_as_a_judge_template.format(
                prompt=item['prompt'].replace('\n', '\\n'),
                response=item['response'].replace('\n', '\\n'),
                document=doc['snippets'][0].replace('\n', '\\n'), # by default, users will only see the first snippet in the UI
            )
            response = client.chat.completions.create(
                # model='gpt-4o-mini-2024-07-18',
                model='gpt-4o-2024-08-06',
                messages=[
                    # {'role': 'system', 'content': llm_as_a_judge_system_message},
                    # {'role': 'user', 'content': user_message},
                    {'role': 'user', 'content': llm_as_a_judge_system_message + '\n\n' + user_message},
                ],
                temperature=0.0,
                max_completion_tokens=1,
            )
            try:
                rating = int(response.choices[0].message.content[-1])
            except:
                rating = None
            doc['rating'] = rating

with open(args.output_path, 'w') as f:
    json.dump(ds, f, indent=4)

avg_rating_top1 = np.mean([doc['rating'] for item in ds for doc in item['docs'][:1]])
avg_rating_top5 = np.mean([doc['rating'] for item in ds for doc in item['docs'][:5]])
ratio_relevant_top1 = np.mean([doc['rating'] >= 2 for item in ds for doc in item['docs'][:1]])
ratio_relevant_top5 = np.mean([doc['rating'] >= 2 for item in ds for doc in item['docs'][:5]])
print(f'Average rating (top-1 documents): {avg_rating_top1:.2f}')
print(f'Average rating (top-5 documents): {avg_rating_top5:.2f}')
print(f'Percentage relevant (top-1 documents): {ratio_relevant_top1 * 100:.2f}%')
print(f'Percentage relevant (top-5 documents): {ratio_relevant_top5 * 100:.2f}%')
