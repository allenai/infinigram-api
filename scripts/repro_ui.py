import requests
import time

prompt = 'Write a short bio for Barack Obama'
response = '''Barack Obama was born on August 4, 1961, in Honolulu, Hawaii, to a Kenyan father, Barack Obama Sr., and an American mother, Stanley Ann Dunham. He grew up in the state and attended local schools, including Punahou School, where he was an outstanding student and athlete. Obama later attended Columbia University in New York City, where he earned a degree in political science.

After graduating, Obama worked as a community organizer in Chicago, where he became involved in local politics and met his future wife, Michelle Robinson. He later attended Harvard Law School, where he became the first African American president of the Harvard Law Review. After graduating, Obama returned to Chicago and practiced civil rights law before entering politics.

Obama was elected to the Illinois State Senate in 1996 and served from 1997 to 2004. In 2004, he was elected to the U.S. Senate, representing the state of Illinois. He gained national attention with his keynote speech at the Democratic National Convention in 2004, which focused on themes of unity, inclusiveness, and hope.

In 2008, Obama ran for President of the United States, winning the election in a historic landslide. He became the first African American to hold the office of President of the United States. During his time in office, Obama implemented a number of significant policy changes, including the Affordable Care Act, the Dodd-Frank Wall Street Reform and Consumer Protection Act, and the legalization of same-sex marriage. He also ordered the military operation that led to the death of Osama bin Laden, the mastermind behind the September 11 attacks.

Obama left office in January 2017, after serving two terms as President. He is the author of several books, including "Dreams from My Father" and "A Promised Land." He currently lives in Chicago with his family.'''

# prompt = 'Why do I need to fact check my results?'
# response = '''Factual mistakes in search results can lead to misinformation, which can have serious consequences in various domains such as decision-making, education, and public safety. By fact-checking your results, you ensure that the information you receive is accurate, unbiased, and relevant, promoting better understanding and reliability in the outcomes.'''

# prompt = 'describe sleep paralysis'
# response = '''Sleep paralysis is a temporary condition in which a person cannot move or speak while falling asleep or waking up. It is a common experience that can be accompanied by vivid and frightening hallucinations, increased heart rate, and feelings of pressure or suffocation.

# Sitting Astride Sleep

# During sleep paralysis, a person is unable to move or speak but is fully aware of their surroundings. This can be a terrifying experience, as the individual feels trapped and powerless. It is often accompanied by vivid and frightening hallucinations, which may be experiences as shadows, monsters, or other forms. It can also be accompanied by a sense of pressure or suffocation, which can be quite intense.

# Somnambulism: Sleepwalking

# Sleep paralysis is sometimes confused with another phenomenon called sleepwalking or somnambulism. Sleepwalking is a disorder in which a person gets out of bed and walks around while still asleep. Unlike sleep paralysis, sleepwalking is not characterized by the inability to move or speak.

# Causes and Risk Factors

# The exact causes and risk factors for sleep paralysis are not yet fully understood. However, it is known to be closely linked to sleep disorders, such as narcolepsy, as well as other conditions that can disrupt an individual's sleep, such as depression, stress, and anxiety.

# Treatment and Prevention

# While sleep paralysis does not have a specific treatment, there are several strategies that can be used to prevent it. These include maintaining a regular sleep schedule, avoiding caffeine and alcohol, and practicing relaxation techniques, such as meditation and deep breathing exercises.

# In cases where sleep paralysis is a symptom of a sleep disorder, such as narcolepsy, treatment of that underlying condition can help to reduce the frequency and severity of episodes.

# For most people, sleep paralysis is a temporary and relatively harmless experience that does not require medical treatment. However, for individuals who experience frequent and severe episodes, it is important to talk to a healthcare provider, such as a sleep specialist, who can help to assess the underlying causes and develop a treatment plan.

# Sharing is caring!'''

# prompt = "can you help me name my first-born child? I'm hoping for a list of names that are modern and unique."
# response = '''Of course! Naming a child is one of the most exciting and memorable experiences for parents. Here is a list of modern and unique names that may fit your criteria:

# Aria: Meaning "air" or "melody," it can be both modern and elegant.
# Brynjar: A combination of "bryn" (meaning "hill" in Old Norse) and "jar" (meaning "warrior" in Old Norse), portrayed as strong and robust.
# Cleo: A short and modern form of the Greek name Cleopatra, meaning "glory of the people."
# Daxin: A unique and modern name, derived from the German word for "association," fitting a child who may have a strong sense of camaraderie or belonging.
# Eleana: A beautiful and unique name derived from the Greek name Helen, meaning "covering," symbolizing protection and nurtorship.
# Elian: A blend of both Hebrew and Welsh origins, named after the legendary Elian character and meaning "elevated" or "splendid."
# Galen: Derived from Galen, the Roman physician and philosopher, this name combines masculine and strong elements.
# Heli: A Hebrew name meaning "sun" and representing light and warmth, fitting for a child who brings joy and harmony.
# Loux: A modern name that means "fox" in Latin, representing cunning and graceful movement.
# Maëlys: A name derived from the French word "maëlle," meaning "apple," with semantic elements of beauty and sweetness.
# Noma: A name that means "fearless" in an ancient language, representing courage and strength.
# Radley: A simple and yet unique masculine name derived from the Old English word "rade," meaning "riding."
# Randie: A combination of the elements of "rationality" and "kindness."
# Seren: Bird-like and serene, it symbolizes tranquility and beauty.
# Talon: A powerful and modern name, inspired by animals and the swiftness of birds, representing strength and velocity.
# Remember, the name you choose will be your child's first possession, reflecting your and your partner's values, preferences, and dreams. So, when you finalize the name, ensure it resonates with love, grace, and wisdom.'''

# prompt = 'When was Kamala Harris born?'
# response = '''Kamala Harris was born on October 21, 1964, in Oakland, California, USA. She is a prominent American politician and the first Black, South Asian, and South Asian-descended woman to be elected to the United States Senate. She currently serves as the Vice President of the United States, having been elected alongside President Joe Biden in November 2020.'''

# prompt = 'describe a proper english cream tea'
# response = '''A proper English cream tea is a delightful and sophisticated beverage that combines the best of both worlds: the rich, savory flavor of cream and the comforting allure of tea. Here's a detailed breakdown of what makes a proper English cream tea:

# Tea Selection: The first step in making a proper English cream tea is selecting the right tea. A traditional English brand such as Ty-Phillips, Tetley, or Twinings is a good choice. Choose a good quality black tea, such as an Assam, Darjeeling, or Earl Grey.

# Scones: Next, scone selection is crucial. A traditional scone is triangular in shape, light brown, and biscuits with a sweet, crumbly texture. They are usually served with clotted cream and jam. A scone can be made from scratch or purchased from a local bakery or restaurant.

# Clotted Cream: Clotted cream is a type of cream that sits atop useable milk due to the higher fat content. It's thicker and creamier than sweet cream and somewhat resembles whipped cream. One great tip for keeping your clotted cream cool while drinking is to place the cream container in the refrigerator while you serve the scones and tea.

# Sliced Bread or Biscuits (optional): If you prefer, you can serve sliced bread or butter-from-scratch, bottled biscuits with your tea and scones. They are an excellent choice for children or sweet tooths and are quite popular with the masses.

# Preserves and Syrups: Bring your tea to life with a few trimmings. Typically, Longintosh tarts are served alongside the tea in its hot brewed state. Myers' falernum syrup pairs well with elderflower cordial and oranges for a spritzy drink. Preserves made with berries and fruits, such as redcurrants, strawberries, or raspberries, add a fruit infusion and delicious natural sweetness to the tea.

# Upon serving, remember to ask your guest if they prefer their tea sweet or unsweetened, and if they want milk ahead of time. This way, you can accommodate their tastes without spoiling the traditional English cream tea experience.'''

# prompt = "It's info about one workload. But only a few of it's fields. So something like WorkloadInfoMinimum would be good. Do you have other ideas?"
# response = '''That's a great observation. Based on your additional context, I suggest a semantic contraction of the phrase "Workload Info" to create a more concise and descriptive name for the class. Here are five alternative suggestions that incorporate this into the class name:

# WorkloadInfoItem: This name emphasizes the importance of each element of the collection by incorporating "item". It also implies it's a piece of the overall "WorkloadInfo" collection.
# WorkloadInfoTuple: Another approach is to use tuple-related terminology, indicating that the class retains multiple Workload values within the collection.
# WorkloadInfoSnippet: This name refers to a smaller section or piece of a WorkloadInfo collection and emphasizes the idea of a microzen.
# WorkloadInfoPartition: Similar to "snippet," the word "partition" implies a small, manageable segment of a larger structure. It also brings to mind partitioning as a concept used in databases and data structures.
# WorkloadInfoBatch: The term "batch" suggests a group or collection of `Workload` elements, placing emphasis on the package or collection aspect.
# Test these suggestions with your application's context and requirements to find the best name for the WorkloadInfo class. As always, clarity and readability in naming are key.'''

# prompt = 'What is the best watch brand?'
# response = '''The best watch brand depends on personal preferences, needs, and budget, as everyone has unique tastes and requirements. However, if you're looking for a classic and timeless watch brand with a rich history, a Swiss watchmaker like Rolex represents a good choice.

# Rolex is a Swiss luxury brand known for its high-quality timepieces, which are made from high-grade metals like stainless steel, gold, and platinum. Rolex's watches are renowned for their accuracy, durability, and stylish design, making them popular among watch enthusiasts and style icons alike.

# Some other notable watch brands that are considered to be high-quality, stylish, and reliable include:

# Audemars Piguet
# Cartier
# Omega
# Patek Philippe
# Louis Vuitton
# Blancpain
# Longines
# Breitling
# Breguet
# Chronometer
# Ultimately, the best watch brand for you will depend on your preferences, needs, and budget. Many watch brands offer high-quality watches at various price points, so it's essential to research and test out different options to find the right fit for you.'''

# prompt = 'tell me about orcas'
# response = '''Orca, or killer whales, are marine mammals belonging to the family Delphinidae (oceanic dolphins). They are highly intelligent, social marine animals known for their distinctive black and white coloring, tall dorsal fins, and large size. Orcas have various populations distributed across the ocean, and each population may have different diets, behaviors, and social structures.

# Some interesting facts about orcas:

# 1. Appearance: Orcas have a distinctive pattern of black and white pigmentation, with a white or light grey underside and a dark grey or nearly black upper body. They have a stocky body, a large dorsal fin (often larger in males), and a short, broad beak. Their tail fins, called flukes, are paddle-shaped and large.

# 2. Behavior: Orcas are highly social and live in complex social groups called pods. These groups may have anywhere from 6-40 members and exhibit a wide range of social behaviors such as cooperation, communication, and play. Orcas have distinctive calls and use echolocation to navigate and find prey underwater.

# 3. Diet: Orcas have varying diets depending on their specific population. They can be classified into different types:
#     a. Resident Orcas: These orcas primarily feed on fish and occasionally squid. They prefer species such as salmon, cod, and rockfish.
#     b. Transient Orcas: These orcas have a mammal-centric diet and focus on hunting marine mammals such as seals, sea lions, dolphins, and occasionally whales.
#     c. Offshore Orcas: Very little is known about the behaviors and diets of this population as they typically inhabit deep ocean areas and are rarely observed.

# 4. Intelligence: Orcas are considered one of the most intelligent marine mammals. They have large brains relative to their body size, complex social behaviors, and have demonstrated a wide range of problem-solving skills. They are also known for their hunting tactics, which include cooperative strategies to catch prey.

# 5. Threats: Orcas face numerous environmental threats, including pollution, habitat destruction, changes in marine food webs, and human-induced entanglements. In some areas, increased competition for food and other resources due to climate change can also impact orca populations.

# 6. Conservation: Orcas are protected under the Marine Mammal Protection Act in the United States and are listed as a data deficient species on the IUCN Red List, which indicates insufficient information to assess their conservation status.

# One book to further explore orcas and their world is "Beyond Words: What Animals Think and Feel," by Carl Safina.'''

# prompt = 'tell me about grilled cheese'
# response = '''Grilled cheese is a classic comfort food that has been enjoyed by people of all ages for centuries. It consists of two slices of bread and cheese, typically used American cheese, though other types of cheese can also be used. The bread is then grilled or fried, resulting in a crispy, golden brown exterior and a gooey, melted interior.

# There are many variations and traditions when it comes to making grilled cheese. Some people prefer to use butter to grease the pan, while others may use oil or cooking spray. The cheese can be applied directly to the bread or placed in between two slices. Some people also add toppings such as tomato, pickles, or ham.

# Grilled cheese is typically served as a snack or light meal, but it can also be a main dish if paired with a salad or soup. The sandwich is often served warm, making it a great option for a quick, satisfying meal.

# Grilled cheese has a long history and can be traced back to ancient Egypt and Rome. In the early 1900s, grilled cheese sandwiches became popular in American diners and began to be served with tomato soup. Today, grilled cheese is a beloved comfort food around the world and continues to be a favorite of people of all ages.'''

payload = {
    'prompt': prompt,
    'response': response,
    'delimiters': ['\n', '.'],
    'allowSpansWithPartialWords': False,
    'minimumSpanLength': 1,
    'maximumFrequency': 10,
    'maximumSpanDensity': 0.05,
    'spanRankingMethod': 'length',
    'includeDocuments': True,
    'maximumDocumentsPerSpan': 10,
    'maximumDocumentDisplayLength': 100,
    'filterMethod': 'bm25',
    'filterBm25FieldsConsidered': 'response',
    'filterBm25RatioToKeep': 1.0,
    'includeInputAsTokens': True,
}

url = 'https://infinigram-api.allen.ai/olmoe/attribution'

result = requests.post(url, json=payload).json()

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

for i in range(5):
    print(deduped_docs[i])
    print()
