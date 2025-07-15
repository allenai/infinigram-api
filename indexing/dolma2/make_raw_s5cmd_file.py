import gzip
import csv
import glob

csv_paths = list(sorted(glob.glob(f'/data_c/tokenized/**/*.csv.gz', recursive=True)))
raw_s3_paths = []

for csv_path in csv_paths:
    with gzip.open(csv_path, 'rt') as f:
        reader = csv.reader(f)
        for row in reader:
            raw_s3_path = row[3]
            raw_s3_paths.append(raw_s3_path)

with open(f's5cmd_files/raw.s5cmd', 'w') as f:
    for raw_s3_path in raw_s3_paths:
        assert raw_s3_path.startswith('s3://')
        raw_local_path = raw_s3_path.replace('s3://', '/data_c/raw/')
        f.write(f'cp {raw_s3_path} {raw_local_path}\n')
