import csv
import os
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--csv-path', type=str, required=True)
parser.add_argument('--output-dir', type=str, required=True)
args = parser.parse_args()

LIMIT = int(1e12) # 1TB = 250B uint32 tokens

with open(args.csv_path) as f:
    reader = csv.DictReader(f)
    rows = list(reader)

S3_PREFIX = 's3://ai2-llm/preprocessed/'
LOCAL_PREFIX = '/data_c/tokenized/'
OUTPUT_DIR = args.output_dir

def write_shard(shard_ix, npy_paths):
    with open(f'{OUTPUT_DIR}/shard_{shard_ix:02d}.s5cmd', 'w') as f:
        for npy_path in npy_paths:
            assert npy_path.startswith(S3_PREFIX)
            local_npy_path = LOCAL_PREFIX + npy_path[len(S3_PREFIX):]
            f.write(f'cp {npy_path} {local_npy_path}\n')

            assert npy_path.endswith('.npy')
            csv_path = npy_path[:-len('.npy')] + '.csv.gz'
            local_csv_path = LOCAL_PREFIX + csv_path[len(S3_PREFIX):]
            f.write(f'cp {csv_path} {local_csv_path}\n')

os.makedirs(OUTPUT_DIR, exist_ok=True)

shard_ix = 0
curr_npy_paths = []
curr_size = 0
for row in rows:
    npy_path = row['key']
    size = int(row['size'])
    assert 0 <= size <= LIMIT
    if curr_size + size > LIMIT:
        write_shard(shard_ix, curr_npy_paths)
        shard_ix += 1
        curr_npy_paths = []
        curr_size = 0
    curr_npy_paths.append(npy_path)
    curr_size += size
if curr_npy_paths != []:
    write_shard(shard_ix, curr_npy_paths)
