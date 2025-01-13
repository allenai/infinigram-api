import csv
import json
from scipy.stats import spearmanr

human_scores_by_thread_id = {}
with open('bailey100_annotation.csv') as f:
    reader = csv.DictReader(f)
    for row in reader:
        thread_id = row['URL'].split('/')[-1]
        scores = [int(row[f'doc #{i}']) for i in range(1, 6)]
        human_scores_by_thread_id[thread_id] = scores

all_human_scores = []
all_llm_scores = []
with open('bailey100_baseline_gpt-4o-2024-08-06_user_rubric.json') as f:
    ds = json.load(f)
    for item in ds:
        thread_id = item['thread_id']
        human_scores = human_scores_by_thread_id[thread_id]
        llm_scores = [doc['rating'] for doc in item['docs']]
        assert len(human_scores) == len(llm_scores)
        all_human_scores.extend(human_scores)
        all_llm_scores.extend(llm_scores)

# compute the spearman correlation
correlation, p_value = spearmanr(all_human_scores, all_llm_scores)
print(f'Spearman correlation: {correlation:.2f}')
