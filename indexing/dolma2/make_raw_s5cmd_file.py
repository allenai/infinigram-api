import gzip
import csv
import glob
from tqdm import tqdm
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--s5cmd-output-path", type=str, default="s5cmd_files_v02/raw.s5cmd")
args = parser.parse_args()


# Dolma3-dolmino-official prefixes
DOLMA3_DOLMINO_PREFIXES = [
]

csv_paths = list(sorted(glob.glob(f'/data_c/tokenized/**/*.csv.gz', recursive=True)))
raw_s3_paths = set()

for csv_path in tqdm(csv_paths):
    with gzip.open(csv_path, 'rt') as f:
        reader = csv.reader(f)
        for row in reader:
            raw_s3_path = row[3]
            if raw_s3_path not in raw_s3_paths:
                raw_s3_paths.add(raw_s3_path)

with open(args.s5cmd_output_path, 'w') as f:
    for raw_s3_path in raw_s3_paths:
        if raw_s3_path.startswith('s3://'):
            pass
        elif 'pretraining-data' in raw_s3_path: # stack-edu, s2pdf
            raw_s3_path = 's3://ai2-llm/pretraining-data' + 'pretraining-data'.join(raw_s3_path.split('pretraining-data')[1:])
        elif '/mnt/raid0/pdfs-reshard/software_dev/' in raw_s3_path:
            raw_s3_path = raw_s3_path.replace('/mnt/raid0/pdfs-reshard/software_dev/', 's3://ai2-llm/pretraining-data/sources/s2pdf_dedupe_minhash_v1_with_no_pii_basic_quality_datadelve_norefs_mdtables_v2_denylisted_reshard/software_dev/')
        elif '/mnt/raid0/pdfs-reshard/software/' in raw_s3_path:
            raw_s3_path = raw_s3_path.replace('/mnt/raid0/pdfs-reshard/software/', 's3://ai2-llm/pretraining-data/sources/s2pdf_dedupe_minhash_v1_with_no_pii_basic_quality_datadelve_norefs_mdtables_v2_denylisted_reshard/software/')
        elif raw_s3_path.startswith('/mnt/raid0/dolmino-official-flat'):
            raw_s3_path = raw_s3_path.replace('/mnt/raid0/dolmino-official-flat', 's3://ai2-llm/pretraining-data/sources/dolma3-dolmino-official/100B')
        else:
            raise NotImplementedError(f'{raw_s3_path} is not supported')
        assert raw_s3_path.startswith('s3://'), raw_s3_path
        raw_local_path = raw_s3_path.replace('s3://', '/data_c/raw/')
        f.write(f'cp {raw_s3_path} {raw_local_path}\n')
