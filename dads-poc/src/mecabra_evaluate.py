#!/usr/bin/env python3
"""TSV (reading, target) -> JSON Lines. Engine enumeration rank, NOT GUI rank."""
import argparse
import collections
import csv
import json
import pathlib
import subprocess
import sys
import unicodedata

def nfc(s):
    return unicodedata.normalize('NFC', s)

def classify(raw, target, top_n):
    reading = nfc(raw['reading'])
    unique = []
    seen = set()
    for c in raw['candidates']:
        # Exclude partial-input candidates and predictive reading extensions.
        if nfc(c['analysis_reading']) != reading or nfc(c['dictionary_reading']) != reading:
            continue
        surface = nfc(c['surface'])
        if surface in seen:
            continue
        seen.add(surface)
        unique.append({**c, 'rank': len(unique) + 1})
    hit = next((c for c in unique if nfc(c['surface']) == nfc(target)), None)
    rank = hit['rank'] if hit else None
    status = ('top1' if rank == 1 else 'topN' if rank and rank <= top_n else
              'beyond_topN' if rank else 'not_observed_exhausted' if raw['enumeration_exhausted']
              else 'not_observed_truncated')
    return {'reading': raw['reading'], 'target': target, 'status': status,
            'rank': rank, 'raw_rank': hit['raw_rank'] if hit else None,
            'top_n': top_n, 'top_candidates': unique[:top_n],
            'full_reading_unique_count': len(unique), 'raw_count': len(raw['candidates']),
            'enumeration_exhausted': raw['enumeration_exhausted'],
            'raw_limit': raw['raw_limit'], 'os': raw['os'], 'guard': raw['guard'],
            'analysis_flags': raw['analysis_flags'], 'input_method_type': raw['input_method_type'],
            'options': raw['options']}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('tsv', type=pathlib.Path)
    parser.add_argument('--top-n', type=int, default=20)
    parser.add_argument('--raw-limit', type=int, default=1000)
    args = parser.parse_args()
    if not 1 <= args.top_n <= args.raw_limit <= 100000:
        parser.error('require 1 <= top-n <= raw-limit <= 100000')
    binary = pathlib.Path(__file__).resolve().parent / 'mecabra_candidates'
    counts = collections.Counter()
    with args.tsv.open(encoding='utf-8-sig', newline='') as f:
        reader = csv.DictReader(f, delimiter='\t')
        if not reader.fieldnames or not {'reading', 'target'} <= set(reader.fieldnames):
            parser.error('TSV needs reading and target headers')
        for line, row in enumerate(reader, 2):
            reading, target = nfc(row.get('reading') or ''), row.get('target') or ''
            try:
                if not target or not 1 <= len(reading) <= 256 or any(
                    not ('\u3041' <= c <= '\u3096' or c == 'ー') for c in reading):
                    raise ValueError('nonempty target and hiragana reading (max 256) required')
                p = subprocess.run([str(binary), reading, str(args.raw_limit)],
                                   capture_output=True, text=True, timeout=35)
                if p.returncode:
                    raise RuntimeError(f'worker exit {p.returncode}: {p.stderr[-2000:]}')
                result = classify(json.loads(p.stdout), target, args.top_n)
            except (OSError, ValueError, RuntimeError, subprocess.TimeoutExpired) as e:
                result = {'reading': reading, 'target': target, 'status': 'error', 'error': str(e)}
            result['line'] = line
            counts[result['status']] += 1
            print(json.dumps(result, ensure_ascii=False), flush=True)
    print(json.dumps(dict(counts), ensure_ascii=False), file=sys.stderr)
    return 1 if counts['error'] else 0

if __name__ == '__main__':
    sys.exit(main())
