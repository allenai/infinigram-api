import requests

# url = 'https://infinigram-api-other-endpoints.allen.ai/olmo-2-0325-32b/find'

# payload = {
#     "query": "multi-step reasoning"
# }

# response = requests.post(url, json=payload)
# print(response.json())

url = 'https://infinigram-api-other-endpoints.allen.ai/olmo-2-0325-32b/get_document_by_rank'

payload = {
    "shard": 0,
    "rank": 259210627240,
    "needle_length": 0,
    "maximum_context_length": 200,
}

response = requests.post(url, json=payload)
print(response.json())
