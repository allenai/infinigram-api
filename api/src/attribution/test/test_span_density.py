import requests

query_factual = '''Kamala Harris is an American politician who served as the junior U.S. Senator from California from 2017 to 2021. Before joining the Senate, Kamala Harris served as the Attorney General of California from 2011 to 2017. she is possibly running for the Democratic nomination for President in the United States presidential election of 2020. Here are some key facts about Kamala Harris:

Early life and education: Kamala Harris was born on October 20, 1964, in Oakland, California, to a Jamaican father and an Indian mother. She graduated from Howard University with a bachelor's degree in political science and UCLA School of Law with a Juris Doctor (JD) degree.
Political career: Harris began her political career serving as the District Attorney of San Francisco from 2003 to 2011. She was the first woman, the first black woman, and the first South Asian American elected as District Attorney for a large city in the United States. In 2010, Kamala Harris was sworn in as California's 34th Attorney General after the incumbent, Jerry Brown, resigned to run for governor. During her tenure as Attorney General, she focused on protecting consumers, defending the state's laws and regulations, and ensuring access to justice for all Californians.
Presidential campaign: In the 2020 presidential election cycle, Harris has declared her candidacy for the Democratic Party's nomination as the President of the United States. She has released a comprehensive plan for tackling COVID-19 aimed at restoring public faith in government, addressing systemic racism, and creating long-term systemic change. She has also proposed a "whole-of-government" approach to increasing access to education and healthcare, providing resources to eyebrows, and restoring the public trust so damaged by the Trump administration.
Personal life: As of November 2021, Harris has one daughter, Maya Harris, born in 2018, with her partner, Doug Emhoff. Harris was openly gay when she was California Attorney General, she was the first person in her role to be openly LGBT. Harris continues to advocate for LGBT and communitarian rights even during her time as a Senator. Her former partner, Shon Baiker, is the mother of her child.
Overall, Kamala Harris is a well-rounded individual with significant political experience and a strong interest in progressive policy reforms, including healthcare, education, criminal justice, and environmental issues.'''

query_creative = '''Tying your shoes is a basic skill that every child learns and every adult should know. Here's a simple guide to help you learn how to tie your shoes:

Begin by holding the laces in each hand, with your fingers spread near the toes ends.
Cross the longer lace over the shorter lace, and place it on top of the shorter lace.
Take the longer lace (on the right) and pass it under the shorter lace, and bring it back up on the other side of the shorter lace.
Pull the longer lace (on the right) through the loop that just appeared briefly, and pull it snug.
Repeat steps 3 and 4 for the other lace.
Cross the longer lace (on the left) over the shorter lace, and place it on top of the shorter lace.
Take the longer lace (on the left and pass it under the shorter lace,) and bring it back up on the other side of the shorter lace.
Pull the longer lace (on the left) through the loop that just appeared briefly, and pull it snug.
At this point, you have crossed the longest laces twice and passed them under the shortest laces twice, so the laces are now tied into a double knot at the top.
Follow these steps again for the other lace or repeat the entire process until you become confident with the tying.
Keep practicing until the laces are easily tied every time. Don't get discouraged if you're having difficulty at first; it takes time and patience to perfect this skill.'''

payload = {
    'query': query_creative,
    'delimiters': ['\n', '.'],
    'maximumSpanDensity': 0.1,
    'minimumSpanLength': 1,
    'maximumFrequency': 10,
    'includeDocuments': False,
    'maximumDocumentDisplayLength': 100,
    'includeInputAsTokens': True,
}

result = requests.post('http://0.0.0.0:8000/pileval-llama/attribution', json=payload).json()
num_spans = len(result['spans'])
num_tokens = len(result['inputTokens'])
density = num_spans / num_tokens if num_tokens > 0 else 0
print(f'Number of spans: {len(result["spans"])}')
print(f'Number of tokens in response: {len(result["inputTokens"])}')
print(f'Span density: {density:.4f} spans per token')
print(f'Span lengths: {list(sorted([span["length"] for span in result["spans"]]))}')
