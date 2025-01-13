import requests
import time

prompt = 'Write a short bio for Barack Obama'
response = '''Barack Obama was born on August 4, 1961, in Honolulu, Hawaii, to a Kenyan father, Barack Obama Sr., and an American mother, Stanley Ann Dunham. He grew up in the state and attended local schools, including Punahou School, where he was an outstanding student and athlete. Obama later attended Columbia University in New York City, where he earned a degree in political science.

After graduating, Obama worked as a community organizer in Chicago, where he became involved in local politics and met his future wife, Michelle Robinson. He later attended Harvard Law School, where he became the first African American president of the Harvard Law Review. After graduating, Obama returned to Chicago and practiced civil rights law before entering politics.

Obama was elected to the Illinois State Senate in 1996 and served from 1997 to 2004. In 2004, he was elected to the U.S. Senate, representing the state of Illinois. He gained national attention with his keynote speech at the Democratic National Convention in 2004, which focused on themes of unity, inclusiveness, and hope.

In 2008, Obama ran for President of the United States, winning the election in a historic landslide. He became the first African American to hold the office of President of the United States. During his time in office, Obama implemented a number of significant policy changes, including the Affordable Care Act, the Dodd-Frank Wall Street Reform and Consumer Protection Act, and the legalization of same-sex marriage. He also ordered the military operation that led to the death of Osama bin Laden, the mastermind behind the September 11 attacks.

Obama left office in January 2017, after serving two terms as President. He is the author of several books, including "Dreams from My Father" and "A Promised Land." He currently lives in Chicago with his family.'''

response = '''1+1=2'''
response = '''1+1 equals 2.'''

payload = {
    'prompt': prompt,
    'response': response,
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

# url = 'http://0.0.0.0:8008/olmoe/attribution'
# url = 'https://infinigram-api.allen.ai/olmoe/attribution'
url = 'http://0.0.0.0:8008/olmo-2-1124-13b/attribution'

start_time = time.time()
result = requests.post(url, json=payload).json()
print(result)
for span in result['spans']:
    print(span['length'], span['unigramLogprobSum'])
latency = time.time() - start_time
print(f'Latency: {latency:.3f} seconds')
