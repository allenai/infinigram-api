import os
import csv
import gzip

# for subset in ['all-dressed-snazzy2/adult_content', 'arxiv', 'finemath-3plus', 's2pdf/adult_content', 'stack-edu/C', 'wikipedia']:
for subset in ['s2pdf/adult_content']:
    print(subset)
    output = os.popen(f'aws s3 cp s3://ai2-llm/preprocessed/dolma2-0625/v0.1/allenai/dolma2-tokenizer/{subset}/000000.csv.gz 000000.csv.gz').read()
    with gzip.open('000000.csv.gz', 'rt') as f:
        reader = csv.reader(f)
        rows = list(reader)
        for row in rows[:10]:
            print(row)
