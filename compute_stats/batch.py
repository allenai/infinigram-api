import argparse
import json
import glob
from tqdm import tqdm
from collections import defaultdict
import os

parser = argparse.ArgumentParser()
parser.add_argument('--data_dir', type=str, required=True)
parser.add_argument('--cpus', type=int, default=1)
parser.add_argument('--workers', type=int, default=1)
parser.add_argument('--output_path', type=str, required=True)
args = parser.parse_args()

doccnt_by_source = defaultdict(int)
doccnt_by_domain_source = defaultdict(int)
doccnt_by_charlen_by_source = defaultdict(lambda: defaultdict(int))

data_paths = glob.glob(f'{args.data_dir}/**/*.json*', recursive=True)
data_paths = list(sorted(data_paths))
for i in tqdm(list(range(0, len(data_paths), args.workers))):
    processes = []
    for j in range(i, min(i + args.workers, len(data_paths))):
        processes.append(os.popen(f'python compute_stats/worker.py --data_dir {args.data_dir} --data_path {data_paths[j]} --cpus {args.cpus // args.workers} --output_path {args.output_path}.tmp.{j}'))
    [p.read() for p in processes]

for j in range(len(data_paths)):
    with open(f'{args.output_path}.tmp.{j}', 'r') as f:
        data = json.load(f)
        for k, v in data['doccnt_by_source'].items():
            doccnt_by_source[k] += v
        for k, v in data['doccnt_by_domain_source'].items():
            doccnt_by_domain_source[k] += v
        for k, v in data['doccnt_by_charlen_by_source'].items():
            for kk, vv in v.items():
                doccnt_by_charlen_by_source[k][kk] += vv

doccnt_by_source = dict(sorted(doccnt_by_source.items(), key=lambda x: x[1], reverse=True))
doccnt_by_domain_source = dict(sorted(doccnt_by_domain_source.items(), key=lambda x: x[1], reverse=True))
doccnt_by_charlen_by_source = {k: dict(sorted(v.items(), key=lambda x: int(x[0]), reverse=False)) for k, v in doccnt_by_charlen_by_source.items()}

with open(args.output_path, 'w') as f:
    json.dump({
        'doccnt_by_source': doccnt_by_source,
        'doccnt_by_domain_source': doccnt_by_domain_source,
        'doccnt_by_charlen_by_source': doccnt_by_charlen_by_source,
    }, f, indent=4)

for j in range(len(data_paths)):
    os.remove(f'{args.output_path}.tmp.{j}')
