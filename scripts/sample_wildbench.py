from datasets import load_dataset
import csv

ds = load_dataset("allenai/WildBench", "v2", split="test")
sample = ds.shuffle(seed=42).select(range(100))

with open('wildbench_sample.csv', 'w') as f:
    fieldnames = ['prompt']
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    for s in sample:
        writer.writerow({'prompt': s["conversation_input"][0]['content']})
