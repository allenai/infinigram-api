import json
from collections import defaultdict
import numpy as np

with open('compute_stats/olmoe-mix-0924.json', 'r') as f:
    js = json.load(f)

with open('../he-olmo-ui/api/dolma_search/static/source_counts/data.json', 'w') as f:
    doccnt_by_source = js['doccnt_by_source']
    total = sum(doccnt_by_source.values())
    json.dump(doccnt_by_source, f)

with open('../he-olmo-ui/api/dolma_search/static/domains/data.json', 'w') as f:
    doccnt_by_domain_source = js['doccnt_by_domain_source']
    doccnt_by_source_by_domain = defaultdict(dict)
    for domain_source, doccnt in list(doccnt_by_domain_source.items())[:20000]:
        source, domain = domain_source.split('/')
        if domain != '':
            doccnt_by_source_by_domain[source][domain] = doccnt
    json.dump(doccnt_by_source_by_domain, f)

with open('../he-olmo-ui/api/dolma_search/static/words/data.json', 'w') as f:
    doccnt_by_charlen_by_source = js['doccnt_by_charlen_by_source']
    bins_by_source = defaultdict(list)
    for source, doccnt_by_charlen in doccnt_by_charlen_by_source.items():
        max_charlen = max([int(charlen) for charlen in doccnt_by_charlen.keys()])
        # [0, 2^0), [2^0, 2^1), [2^1, 2^2), ..., [2^num_bins-1, 2^num_bins)
        num_bins = int(np.log2(max_charlen)) + 2
        counts = [0] * num_bins
        for charlen, doccnt in doccnt_by_charlen.items():
            bin_idx = 0 if charlen == '0' else (int(np.log2(int(charlen))) + 1)
            counts[bin_idx] += doccnt
        bins = [{'min': int(2**(b-1)), 'max': int(2**b), 'doc_count': counts[b], 'percentage': counts[b] / total} for b in range(num_bins)]
        bins_by_source[source] = bins
    json.dump(bins_by_source, f)
