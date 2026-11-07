"""Build accepted dictionary files from review.csv. SPDX-License-Identifier: MIT."""
import csv
import plistlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def main():
    with (ROOT / 'review.csv').open(encoding='utf-8-sig', newline='') as f:
        reader = csv.DictReader(f)
        fields = reader.fieldnames
        rows = list(reader)
    assert len({r['candidate_id'] for r in rows}) == len(rows), 'Duplicate candidate IDs'
    assert all(r['status'] in ('採用', '不採用', '保留', '未確認') for r in rows)
    accepted = [r for r in rows if r['status'] == '採用']
    pairs = [(r['reading'], r['surface']) for r in accepted]
    assert len(set(pairs)) == len(pairs), 'Duplicate reading/form pairs'
    assert all(0 < len(a) <= 32 and 0 < len(b) <= 64 for a, b in pairs), 'Invalid lengths'
    assert all(not any(c in a+b for c in '\n\r\t\x00') for a,b in pairs), 'Invalid control characters'
    entries = [{'phrase': b, 'shortcut': a} for a, b in pairs]
    target = ROOT / 'mac-install-129' / 'DADS_採用129件_ユーザ辞書.plist'
    target.parent.mkdir(exist_ok=True)
    target.write_bytes(plistlib.dumps(entries, sort_keys=False))
    assert plistlib.loads(target.read_bytes()) == entries
    with (ROOT / 'dictionary.csv').open('w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(accepted)
    print(f'{len(rows)} reviewed pairs; {len(entries)} accepted pairs exported')

if __name__ == '__main__':
    main()
