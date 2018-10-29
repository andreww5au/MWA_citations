#!/usr/bin/env python
import json
import numpy as np


def sum_file(file):
    with open(file, 'r') as f:
        d = json.load(f)
        s = np.sum([v['v'] for v in d['rows'][-1]['c'][1:]])
    return s


print('Total cites from MWA papers: ', sum_file('MWA.json'))
print('Total cites from External papers: ', sum_file('MWA-external.json'))
print('Total cites from pre-MWA papers: ', sum_file('pre-MWA.json'))
print('Total cites from all papers: ', sum_file('MWA-all.json'))
