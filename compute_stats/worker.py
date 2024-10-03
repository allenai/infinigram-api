import argparse
import gzip
import zstandard as zstd
import json
from collections import defaultdict
import multiprocessing as mp

parser = argparse.ArgumentParser()
parser.add_argument('--data_dir', type=str, required=True)
parser.add_argument('--data_path', type=str, required=True)
parser.add_argument('--cpus', type=int, default=1)
parser.add_argument('--output_path', type=str, required=True)
args = parser.parse_args()

def load_file(path):
    if path.endswith('.gz'):
        with gzip.open(path, 'rt', encoding='utf-8') as f:
            lines = f.readlines()
    elif path.endswith('.zst'):
        with open(path, 'rb') as f:
            dctx = zstd.ZstdDecompressor()
            with dctx.stream_reader(f) as reader:
                decompressed_data = reader.read().decode('utf-8')
            lines = decompressed_data.split('\n')
            if lines[-1] == '':
                lines = lines[:-1]
    elif path.endswith('.jsonl'):
        with open(path, encoding='utf-8') as f:
            lines = f.readlines()
    else:
        raise ValueError(f'Unknown file type: {path}')
    return lines

def process(line):
    item = json.loads(line.strip('\n'))
    try:
        domain = item['metadata']['url'].split('/')[2]
    except:
        domain = ''
    return domain, len(item['text'])

doccnt_by_source = defaultdict(int)
doccnt_by_domain_source = defaultdict(int)
doccnt_by_charlen_by_source = defaultdict(lambda: defaultdict(int))

with mp.get_context('fork').Pool(args.cpus) as p:
    source = args.data_path[len(args.data_dir)+1:].split('/')[0]
    lines = load_file(args.data_path)
    results = p.map(process, lines)
    for (domain, charlen) in results:
        doccnt_by_source[source] += 1
        doccnt_by_domain_source[f'{source}/{domain}'] += 1
        doccnt_by_charlen_by_source[source][charlen] += 1

doccnt_by_source = dict(sorted(doccnt_by_source.items(), key=lambda x: x[1], reverse=True))
doccnt_by_domain_source = dict(sorted(doccnt_by_domain_source.items(), key=lambda x: x[1], reverse=True))
doccnt_by_charlen_by_source = {k: dict(sorted(v.items(), key=lambda x: int(x[0]), reverse=False)) for k, v in doccnt_by_charlen_by_source.items()}

with open(args.output_path, 'w') as f:
    json.dump({
        'doccnt_by_source': doccnt_by_source,
        'doccnt_by_domain_source': doccnt_by_domain_source,
        'doccnt_by_charlen_by_source': doccnt_by_charlen_by_source,
    }, f, indent=4)
