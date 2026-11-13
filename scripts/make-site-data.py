#!/usr/bin/env python3
#
# Usage:
# $ scripts/make-site-data.py
#
# Writes docs/data/sentences.json from tables/all.csv: for each AIDA sentence,
# the sources linked to it and their relations. The website's sentence pages
# use this file to list the sources of a sentence.
#

import csv
import json
import os
import sys

sentences = {}
sources = set()

with open('tables/all.csv', newline='', encoding='utf-8') as f:
    for row in csv.DictReader(f):
        link = [row['RELATION'], row['SOURCE']]
        links = sentences.setdefault(row['AIDA-SENTENCE'], [])
        if link not in links:
            links.append(link)
        sources.add(row['SOURCE'])

os.makedirs('docs/data', exist_ok=True)

# One sentence per line, sorted, so that changes show up as readable diffs.
with open('docs/data/sentences.json', 'w', encoding='utf-8') as f:
    f.write('{"sentences": {\n')
    f.write(',\n'.join(
        json.dumps(s, ensure_ascii=False) + ': '
        + json.dumps(sentences[s], ensure_ascii=False, separators=(',', ':'))
        for s in sorted(sentences)
    ))
    f.write('\n}}\n')

print(f'{len(sentences)} sentences from {len(sources)} sources', file=sys.stderr)
