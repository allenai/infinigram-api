import csv
import requests

query_obama = '''Barack Hussein Obama II was born on August 4, 1961, in Honolulu, Hawaii. He is the 44th President of the United States, serving two terms from January 20, 2009, to January 20, 2017. An African-American, Obama is the first African descent or first person of any race to hold the office of the President.

Obama graduated from Columbia University in 1983 and Harvard Law School in 1989. He stayed in Boston for some time before returning to Chicago, where he worked as a civil rights lawyer and community organizer. In 2004, Obama ran for the U.S. Senate and won, representing Illinois. Successfully running for President in 2008, Obama took office in January 2009.

Throughout his tenure as President, Barack Obama oversaw the recovery from the 2008 financial crisis and the 2008-2010 Great Recession. He pushed for health care reform, signing the Affordable Care Act, and strived to lessen racial tension in society. He also led military missions against terrorism organizations worldwide during his presidency. Obama retired from politics after completing his second term, but his impact and contributions have sustained him as a powerful and influential figure.

On November 10, 2020, Barack Obama flipped Massachusetts, which he once represented as a Senator, to Biden in the Presidential race. More recently, in October 2021, Barack Obama gave one of the most celebrated speeches of the year in Las Vegas, Nevada, in support of Democratic candidates up and down the ballots.'''

query_biden = '''Joseph Robinette "Joe" Biden Jr. was born on November 20, 1942, in Scranton, Pennsylvania. He is the 47th Vice President of the United States, serving under President Barack Obama from 2009 to 2017. Biden, a Democrat, represented Delaware in the U.S. Senate for 36 years before becoming vice president.

Biden earned a reputation as a respected and trusted bipartisan figure, working with both Republicans and Democrats in the Senate. He passed major legislation during his time in Congress, including the Children's Health Insurance Program and the Violence Against Women Act. In 2008, he ran unsuccessfully for the Democratic nomination for U.S. President.

In 2009, after Barack Obama became President, he selected Biden to be his vice president. Biden is the oldest person and the first Roman Catholic to serve as U.S. Vice President. During his tenure as Vice President, he saw the country navigate various challenges such as enforcing the Affordable Care Act, managing the Obama administration's relations with Iran, facing the 2010 midterm election victories by the Republican Party, experiencing the ceasefire in the Israel-Gaza conflict, losing close friend and former senator Ted Kennedy, and many others.

Biden was often described as a ringing voice of reason and a calming influence in The White House, working closely with the President daily. Strongly connected to the people, he has numerous public appearances nationally and internationally, promoting the America recovery, security, and improved international relations.

Biden retired at the end of his Vice Presidential term, closing a 33-year Senate journey, and returned to his hometown where he plans to focus on his role as Chairman of the Democratic national committee, involved with the party strategy and organization.'''

query_queen = '''Queen Elizabeth II, full name Elizabeth Alexandra Mary, is the reigning monarch of the United Kingdom and 14 other Commonwealth countries. She was born on April 21, 1926, in London, to Prince Albert (future King Albert II), Duke of York, and Elizabeth Bowes-Lyon. If her father had not died early, Elizabeth would not have ascended to the throne. but with his sudden death on November 14, 1936, as a result, Elizabeth became the heir apparent and Queen of eight countries.

When Elizabeth was just a princess, her life dramatically changed on May 27, 1940. In what became known as the trio's escape, Hitler's Nazi forces near London threatened by German bombs, and her family was relocated several times. Later on, her family took residence at the Royal Lodge in Windsor Great Park. She graduated from the Royal Montagu School, now known as Beaumont, in 1944. On July 23, 1947, Elizabeth married Philip Mountbatten, Duke of Edinburgh, and they assumed the joint style of Arches and 575th of the Order of the Garter. They had four children over the years -- Charles, Anne, Andrew, and Edward -- who all (except for Edward) became a part of the UK's Royal Navy or Royal Air Force.

Elizabeth acceded to the throne of the United Kingdom on February 6, 1952, upon the death of her father King George VI. As the longest-reigning British monarch, she has overseen significant changes in the United Kingdom, Britain's Colonies and dominions gained independence; some no longer use "Queen" in their titles, like Canada, Australia, and New Zealand. Elizabeth II celebrated her platinum jubilee -- meanings sixtieth anniversary of her ascension -- in February 2022.'''

query_harris = '''Kamala Harris is an American politician who served as the junior U.S. Senator from California from 2017 to 2021. Before joining the Senate, Kamala Harris served as the Attorney General of California from 2011 to 2017. she is possibly running for the Democratic nomination for President in the United States presidential election of 2020. Here are some key facts about Kamala Harris:

Early life and education: Kamala Harris was born on October 20, 1964, in Oakland, California, to a Jamaican father and an Indian mother. She graduated from Howard University with a bachelor's degree in political science and UCLA School of Law with a Juris Doctor (JD) degree.
Political career: Harris began her political career serving as the District Attorney of San Francisco from 2003 to 2011. She was the first woman, the first black woman, and the first South Asian American elected as District Attorney for a large city in the United States. In 2010, Kamala Harris was sworn in as California's 34th Attorney General after the incumbent, Jerry Brown, resigned to run for governor. During her tenure as Attorney General, she focused on protecting consumers, defending the state's laws and regulations, and ensuring access to justice for all Californians.
Presidential campaign: In the 2020 presidential election cycle, Harris has declared her candidacy for the Democratic Party's nomination as the President of the United States. She has released a comprehensive plan for tackling COVID-19 aimed at restoring public faith in government, addressing systemic racism, and creating long-term systemic change. She has also proposed a "whole-of-government" approach to increasing access to education and healthcare, providing resources to eyebrows, and restoring the public trust so damaged by the Trump administration.
Personal life: As of November 2021, Harris has one daughter, Maya Harris, born in 2018, with her partner, Doug Emhoff. Harris was openly gay when she was California Attorney General, she was the first person in her role to be openly LGBT. Harris continues to advocate for LGBT and communitarian rights even during her time as a Senator. Her former partner, Shon Baiker, is the mother of her child.
Overall, Kamala Harris is a well-rounded individual with significant political experience and a strong interest in progressive policy reforms, including healthcare, education, criminal justice, and environmental issues.'''

query_shoe = '''Tying your shoes is a basic skill that every child learns and every adult should know. Here's a simple guide to help you learn how to tie your shoes:

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
    'query': query_obama,
    'delimiters': ['\n', '.'],
    'maximumSpanDensity': 0.05,
    'minimumSpanLength': 1,
    'maximumFrequency': 10,
    'includeDocuments': True,
    'maximumDocumentDisplayLength': 100,
    'includeInputAsTokens': True,
    'filterMethod': 'bm25',
}

result = requests.post('http://0.0.0.0:8000/dolma-1_7/attribution', json=payload).json()
num_spans = len(result['spans'])
num_tokens = len(result['inputTokens'])
density = num_spans / num_tokens if num_tokens > 0 else 0
num_docs = sum(len(span['documents']) for span in result['spans'])
print(f'Number of spans: {len(result["spans"])}')
print(f'Number of tokens in response: {len(result["inputTokens"])}')
print(f'Span density: {density:.4f} spans per token')
print(f'Span lengths: {list(sorted([span["length"] for span in result["spans"]]))}')
print(f'Total number of documents: {num_docs}')

for s, span in enumerate(result['spans']):
    print(f'Span {s}: {span["text"]}')
    documents = span['documents']
    print(len(documents))
    for d, doc in enumerate(documents):
        print('--------' * 10)
        print(f'Document {d}: shard={doc["shard"]}, pointer={doc["pointer"]}, score={doc.get("score", ""):.4f}, text={doc["text"] if "text" in doc else ""}')
    print('========' * 10)

with open('csv/obama_100.csv', 'w') as f:
    writer = csv.DictWriter(f, fieldnames=['span_ix', 'span_text', 'doc_text', 'score', 'label', 'score > thresh?'])
    writer.writeheader()
    for s, span in enumerate(result['spans']):
        for d, doc in enumerate(span['documents']):
            writer.writerow({
                'span_ix': s if d == 0 else '',
                'span_text': span['text'] if d == 0 else '',
                'doc_text': doc['text'],
                'score': f"{doc.get('score', ''):.4f}",
                'label': '',
                'score > thresh?': '',
            })
