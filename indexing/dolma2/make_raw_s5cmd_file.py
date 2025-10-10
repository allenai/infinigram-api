import gzip
import csv
import glob
from tqdm import tqdm

csv_paths = list(sorted(glob.glob(f'/data_c/tokenized/**/*.csv.gz', recursive=True)))
raw_s3_paths = set()

for csv_path in tqdm(csv_paths):
    with gzip.open(csv_path, 'rt') as f:
        reader = csv.reader(f)
        for row in reader:
            raw_s3_path = row[3]
            if raw_s3_path not in raw_s3_paths:
                raw_s3_paths.add(raw_s3_path)

with open(f's5cmd_files/raw.s5cmd', 'w') as f:
    for raw_s3_path in raw_s3_paths:
        if raw_s3_path.startswith('s3://'):
            pass
        elif 'pretraining-data' in raw_s3_path: # stack-edu, s2pdf
            raw_s3_path = 's3://ai2-llm/pretraining-data' + 'pretraining-data'.join(raw_s3_path.split('pretraining-data')[1:])
        else:
            raise NotImplementedError(f'{raw_s3_path} is not supported')
        if 'cc_all_dressed/all_dressed_v3/weborganizer_ft/dclm_plus2_vigintiles/data/' in raw_s3_path:
            og_raw_s3_path = raw_s3_path
            # e.g. s3://ai2-llm/pretraining-data/sources/cc_all_dressed/all_dressed_v3/weborganizer_ft/dclm_plus2_vigintiles/data/adult_content/vigintile_0018/shard_00000192.jsonl.zst
            # should be s3://ai2-llm/pretraining-data/sources/dolma2-0625-official/common_crawl-adult_content-0018/shard_00000192.jsonl.zst
            raw_s3_path = raw_s3_path.replace('cc_all_dressed/all_dressed_v3/weborganizer_ft/dclm_plus2_vigintiles/data/', 'dolma2-0625-official/common_crawl-')
            raw_s3_path = raw_s3_path.replace('/vigintile_', '-')
            assert raw_s3_path.startswith('s3://'), raw_s3_path
            raw_local_path = og_raw_s3_path.replace('s3://', '/data_c/raw/')
            f.write(f'cp {raw_s3_path} {raw_local_path}\n')

        else:   
            assert raw_s3_path.startswith('s3://'), raw_s3_path
            raw_local_path = raw_s3_path.replace('s3://', '/data_c/raw/')
            f.write(f'cp {raw_s3_path} {raw_local_path}\n')
