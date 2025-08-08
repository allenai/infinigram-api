import json
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
sns.set_theme(style='whitegrid')

with open('data/bailey100_newhparams.json') as f:
    ds = json.load(f)


# span lengths
span_lengths = []
for item in ds:
    for span in item['spans']:
        span_length = len(span['tokenIds'])
        span_lengths.append(span_length)

# print(f'mean: {np.mean(span_lengths):.2f}')
# print(f'median: {np.median(span_lengths):.2f}')
# print(f'min: {np.min(span_lengths):.2f}')
# print(f'max: {np.max(span_lengths):.2f}')

plt.figure(figsize=(3.5, 3.5))
bins = np.arange(5, 22, 1)
plt.hist(span_lengths, bins=bins, range=(5, 22), align='left', rwidth=0.8)
# add vertical line at mean
plt.axvline(np.mean(span_lengths), color='black', linestyle='--', label='mean')
# annotate mean
plt.text(np.mean(span_lengths) + 0.5, plt.ylim()[1] * 0.8, f'mean: {np.mean(span_lengths):.1f}', fontsize=12, color='black')
plt.xlabel('span length (tokens)')
plt.ylabel('frequency')
plt.title('Distribution of length of spans')
plt.savefig('scripts/stat_span_len.png', dpi=300, bbox_inches='tight')


# relevance scores
from rank_bm25 import BM25Okapi
doc_results = []
span_results = []
for item in ds:
    docs = [doc['text'] for span in item['spans'] for doc in span['documents']]
    tokenized_corpus = [doc.split(" ") for doc in docs]
    bm25 = BM25Okapi(tokenized_corpus)
    doc_scores = bm25.get_scores((item['prompt'] + " " + item["response"]).split(" "))
    for doc, score in zip(docs, doc_scores):
        doc_results.append({
            'response_len_chars': len(item['response']),
            'score': score,
            'is_max_in_thread': score == max(doc_scores),
        })
    offset = 0
    for span in item['spans']:
        score = max(doc_scores[offset:offset+len(span['documents'])])
        span_results.append({
            'response_len_chars': len(item['response']),
            'score': score,
            'is_max_in_thread': score == max(doc_scores),
        })
        offset += len(span['documents'])

maxlen = 5000
max_multiplier = 0.18
high_multiplier = 0.7 * max_multiplier
med_multiplier = 0.5 * max_multiplier

def plot_scores(mode):
    if mode == 'doc':
        results = doc_results
    elif mode == 'span':
        results = span_results
    else:
        raise ValueError(f'Invalid mode: {mode}')

    num_high = len([r for r in results if r['score'] >= high_multiplier * r['response_len_chars']])
    num_med = len([r for r in results if med_multiplier * r['response_len_chars'] <= r['score'] < high_multiplier * r['response_len_chars']])
    num_low = len([r for r in results if r['score'] < med_multiplier * r['response_len_chars']])
    perc_high = num_high / len(results)
    perc_med = num_med / len(results)
    perc_low = num_low / len(results)

    plt.figure(figsize=(5, 5))
    plt.fill_between([0, maxlen], [0, high_multiplier * maxlen], [max_multiplier * maxlen, max_multiplier * maxlen], color='green', alpha=0.5)
    plt.text(500, 550, f'high relevance\n({int(round(perc_high * 100))}%)', fontsize=14, color='black')
    plt.fill_between([0, maxlen], [0, med_multiplier * maxlen], [0, high_multiplier * maxlen], color='green', alpha=0.3)
    plt.text(4500, 460, f'medium\nrelevance\n({int(round(perc_med * 100))}%)', fontsize=14, color='black')
    plt.fill_between([0, maxlen], [0, 0], [0, med_multiplier * maxlen], color='green', alpha=0.1)
    plt.text(3000, 30, f'low relevance\n({int(round(perc_low * 100))}%)', fontsize=14, color='black')
    plt.scatter([r['response_len_chars'] for r in results], [r['score'] for r in results], label=f'{mode}')
    plt.scatter([r['response_len_chars'] for r in results if r['is_max_in_thread']], [r['score'] for r in results if r['is_max_in_thread']], label=f'{mode} with max score in thread')
    plt.plot([0, maxlen], [0, max_multiplier * maxlen], 'k--', label=f'soft upper bound for {mode} score')
    plt.xlabel('response length (chars)')
    plt.ylabel(f'BM25 score')
    plt.legend()
    plt.title(f'Relevance scores of {"documents" if mode == "doc" else "spans"}')
    plt.savefig(f'scripts/stat_score_{mode}.png', dpi=300, bbox_inches='tight')

plot_scores('doc')
plot_scores('span')


# training stage
num_pre = 0
num_mid = 0
num_post = 0
num_post_sft = 0
num_post_dpo = 0
num_post_rlvr = 0
for item in ds:
    for span in item['spans']:
        for doc in span['documents']:
            path = doc['metadata']['path']
            if 'rlvr' in path.lower():
                num_post_rlvr += 1
                num_post += 1
            elif 'preference' in path.lower():
                num_post_dpo += 1
                num_post += 1
            elif 'sft' in path.lower():
                num_post_sft += 1
                num_post += 1
            elif 'dolmino' in path.lower():
                num_mid += 1
            else:
                num_pre += 1
num_total = num_pre + num_mid + num_post

print(f'pre: {num_pre / num_total * 100:.2f}%')
print(f'mid: {num_mid / num_total * 100:.2f}%')
print(f'post: {num_post / num_total * 100:.2f}%')
print(f'post_sft: {num_post_sft / num_total * 100:.2f}%')
print(f'post_dpo: {num_post_dpo / num_total * 100:.2f}%')
print(f'post_rlvr: {num_post_rlvr / num_total * 100:.2f}%')
