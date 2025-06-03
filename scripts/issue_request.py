import requests
import time

prompt = 'Write a short bio for Barack Obama'
response = '''Barack Obama was born on August 4, 1961, in Honolulu, Hawaii, to a Kenyan father, Barack Obama Sr., and an American mother, Stanley Ann Dunham. He grew up in the state and attended local schools, including Punahou School, where he was an outstanding student and athlete. Obama later attended Columbia University in New York City, where he earned a degree in political science.

After graduating, Obama worked as a community organizer in Chicago, where he became involved in local politics and met his future wife, Michelle Robinson. He later attended Harvard Law School, where he became the first African American president of the Harvard Law Review. After graduating, Obama returned to Chicago and practiced civil rights law before entering politics.

Obama was elected to the Illinois State Senate in 1996 and served from 1997 to 2004. In 2004, he was elected to the U.S. Senate, representing the state of Illinois. He gained national attention with his keynote speech at the Democratic National Convention in 2004, which focused on themes of unity, inclusiveness, and hope.

In 2008, Obama ran for President of the United States, winning the election in a historic landslide. He became the first African American to hold the office of President of the United States. During his time in office, Obama implemented a number of significant policy changes, including the Affordable Care Act, the Dodd-Frank Wall Street Reform and Consumer Protection Act, and the legalization of same-sex marriage. He also ordered the military operation that led to the death of Osama bin Laden, the mastermind behind the September 11 attacks.

Obama left office in January 2017, after serving two terms as President. He is the author of several books, including "Dreams from My Father" and "A Promised Land." He currently lives in Chicago with his family.'''

# response = '''Barack Obama is a prominent figure in American and global politics, best known for serving as the 44th President of the United States from January 20, 2009, to January 20, 2017. Born on August 4, 1961, in Honolulu, Hawaii, Obama is a graduate of Columbia University and Harvard Law School. His political career began as a community organizer in Chicago before becoming a civil rights attorney, a professor of constitutional law, and then a State Senator representing the 13th District of Illinois from 1997 to 2004.

# Obama's rise to national prominence came with his keynote address at the 2004 Democratic National Convention, where he expressed a vision of unity and hope, which resonated with many Americans. This speech earned him the nickname "The Rock Star of Politics" and catapulted him to the forefront of Democratic politics. In 2008, he became the first African American to be elected President of the United States, campaigning on a message of "hope and change" and promising to end the Iraq War, tackle climate change, and reform healthcare.

# As president, Obama signed into law the Affordable Care Act (ACA), which aimed to increase the affordability and coverage of health insurance, and also repealed the military's "Don't Ask, Don't Tell" policy, allowing LGBTQ individuals to serve openly in the military. His administration also played a key role in the response to the Great Recession, overseeing the rescue of the auto industry, the Dodd-Frank Wall Street Reform and Consumer Protection Act, and the implementation of the American Recovery and Reinvestment Act.

# In foreign policy, Obama's administration normalized relations with Cuba, negotiated the Iran nuclear deal, ordered the raid that led to the killing of Osama bin Laden, and worked to broker a ceasefire in the Syrian Civil War. His presidency also marked significant advancements in LGBTQ rights, with the legalization of same-sex marriage nationwide by the Supreme Court in 2015.

# After leaving office, Obama has been involved in public speaking, writing, and philanthropy. He and his wife, Michelle Obama, have worked on various projects through their Obama Foundation, which seeks to empower communities through education and leadership. Barack Obama's legacy as a transformative figure in American politics and his enduring popularity make him one of the most influential political figures of his generation.'''

# response = '''The trace function is invariant under cyclic permutations, so:

# [ \mathrm{tr}(\mathbf{A}^{-1}, \mathbf{A}^{-T}) = \mathrm{tr}(\mathbf{A}^{-T}, \mathbf{A}^{-1}) = (\mathbf{A}^{-1})^\\top \mathbf{A}^{-1} ]

# Let ( \mathbf{B} = \mathbf{A}^{-1} ). Then ( f(\mathbf{A}) = \mathrm{tr}(\mathbf{B}, \mathbf{B}^\\top) ).'''
# print(response)

# prompt = '''Count from 1 to 100, one number at a time'''
# response = '''1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100.'''

# prompt = '''Tell me briefly about Jacob Bernoulli'''
# response = '''Jacob Bernoulli (1654–1705) was a Swiss mathematician and a member of the Bernoulli family, which was prominent in the fields of mathematics and science during the 17th and 18th centuries. He is known for his contributions to infinitesimal calculus, probability theory, and mathematical analysis.

# Jacob Bernoulli made significant advancements in the understanding of calculus, which he referred to as "the calculus of infinitesimals." He is credited with the first use of the term "function" in the mathematical sense and with the discovery of the fundamental theorem of calculus, although he did not provide a formal proof. His work laid the groundwork for the development of calculus by later mathematicians such as Isaac Newton and Gottfried Wilhelm Leibniz.

# In probability theory, Bernoulli is known for the Bernoulli distribution and Bernoulli trials, which are foundational concepts in the study of probability and statistics. The Bernoulli distribution describes a random variable that takes the value 1 with probability (p) and the value 0 with probability (1-p). Bernoulli trials refer to a sequence of independent experiments, each with two possible outcomes, often referred to as "success" and "failure."

# Jacob Bernoulli's contributions to mathematics were published posthumously in his book "Ars Conjectandi" (The Art of Conjecturing), which was edited and published by his brother Johann Bernoulli in 1713. This work consolidated his findings in calculus and probability theory and had a lasting impact on the development of these fields.'''

# prompt = '''Count from 1 to 500, one number at a time'''
# response = '''1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 161, 162, 163, 164, 165, 166, 167, 168, 169, 170, 171, 172, 173, 174, 175, 176, 177, 178, 179, 180, 181, 182, 183, 184, 185, 186, 187, 188, 189, 190, 191, 192, 193, 194, 195, 196, 197, 198, 199, 200, 201, 202, 203, 204, 205, 206, 207, 208, 209, 210, 211, 212, 213, 214, 215, 216, 217, 218, 219, 220, 221, 222, 223, 224, 225, 226, 227, 228, 229, 230, 231, 232, 233, 234, 235, 236, 237, 238, 239, 240, 241, 242, 243, 244, 245, 246, 247, 248, 249, 250, 251, 252, 253, 254, 255, 256, 257, 258, 259, 260, 261, 262, 263, 264, 265, 266, 267, 268, 269, 270, 271, 272, 273, 274, 275, 276, 277, 278, 279, 280, 281, 282, 283, 284, 285, 286, 287, 288, 289, 290, 291, 292, 293, 294, 295, 296, 297, 298, 299, 300, 301, 302, 303, 304, 305, 306, 307, 308, 309, 310, 311, 312, 313, 314, 315, 316, 317, 318, 319, 320, 321, 322, 323, 324, 325, 326, 327, 328, 329, 330, 331, 332, 333, 334, 335, 336, 337, 338, 339, 340, 341, 342, 343, 344, 345, 346, 347, 348, 349, 350, 351, 352, 353, 354, 355, 356, 357, 358, 359, 360, 361, 362, 363, 364, 365, 366, 367, 368, 369, 370, 371, 372, 373, 374, 375, 376, 377, 378, 379, 380, 381, 382, 383, 384, 385, 386, 387, 388, 389, 390, 391, 392, 393, 394, 395, 396, 397, 398, 399, 400, 401, 402, 403, 404, 405, 406, 407, 408, 409, 410, 411, 412, 413, 414, 415, 416, 417, 418, 419, 420, 421, 422, 423, 424, 425, 426, 427, 428, 429, 430, 431, 432, 433, 434, 435, 436, 437, 438, 439, 440, 441, 442, 443, 444, 445, 446, 447, 448, 449, 450.'''

# prompt = '''Give me the lyrics of the song "Yesterday" by The Beatles'''
# response = '''Yesterday, all my troubles seemed so far away'''

# prompt = ''
# response = '''Puigdemont calls for talks with Spain Published duration 22 December 2017 Related Topics Catalonia independence protests'''

payload = {
    'response': response,
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

url = 'http://0.0.0.0:8080/pileval-llama/attribution'
# url = 'http://0.0.0.0:8080/olmo-2-1124-13b/attribution'

start_time = time.time()
result = requests.post(url, json=payload).json()
print(result)
# print(result.keys())
# for span in result['spans']:
#     print(span['length'], span['unigramLogprobSum'])
# print('inputTokens:', result['inputTokens'])
# print(result['spans'][0])
for span in result['spans']:
    print(f'l={span["left"]}, r={span["right"]}, count={span["count"]}, text={span["text"]}')
# for span in result['spans']:
#     print('Span text:', span['text'])
#     for doc in span['documents']:
#         print('First document:')
#         print('========')
#         print(f'short version: disp_len={doc["displayLength"]}, needle_offset={doc["needleOffset"]}')
#         print(doc['text'])
#         print('========')
#         print(f'long version: disp_len={doc["displayLengthLong"]}, needle_offset={doc["needleOffsetLong"]}')
#         print(doc['textLong'])
#         break
#     break
latency = time.time() - start_time
print(f'Latency: {latency:.3f} seconds')
