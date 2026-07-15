#!/usr/bin/env python3
"""
Look up MOE code (Ministry of Education learning objective code) for a
methodica unit ID.

Returns two values:
- moe_code       — full MOE learning objective code (7 levels)
- subtopic_code  — MOE code truncated to sub-topic level (6 levels)

Usage:
    python lookup_moe.py <unit-id>
    python lookup_moe.py methodica-math-scale-01

Exits with 0 if found, 1 if not (with a stderr message).
"""

import sys
import io
import json
import argparse
from pathlib import Path

if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    except Exception:
        pass


def load_objectives(path: Path = None):
    if path is None:
        path = Path(__file__).parent.parent / 'references' / 'learning-objectives.json'
    with open(path, encoding='utf-8') as f:
        return json.load(f)


def find_moe(unit_id: str, objectives: dict):
    """Search both math and science lists for the unit_id and return its MOE fields."""
    for subject, entries in objectives.items():
        for e in entries:
            if e['id'] == unit_id:
                return {
                    'moe_code': e.get('moe_code'),
                    'subtopic_code': e.get('subtopic_code'),
                    'topic_he': e.get('topic_he_moe') or e.get('topic'),
                    'subtopic_he': e.get('subtopic_he'),
                    'objective_he': e.get('objective'),
                    'subject': subject,
                }
    return None


def main():
    ap = argparse.ArgumentParser(description='Look up MOE code for a methodica unit ID.')
    ap.add_argument('unit_id', help='Full unit ID like methodica-math-scale-01')
    ap.add_argument('--json', default=None, help='Path to learning-objectives.json')
    ap.add_argument('--format', choices=['json', 'kv'], default='kv',
                    help='Output format: kv (default, key=value lines) or json')
    args = ap.parse_args()

    objectives = load_objectives(Path(args.json) if args.json else None)
    info = find_moe(args.unit_id, objectives)

    if info is None:
        print(f'ERROR: unit ID "{args.unit_id}" not found in learning-objectives.json.',
              file=sys.stderr)
        sys.exit(1)

    if info['moe_code'] is None:
        print(f'WARNING: unit "{args.unit_id}" has no MOE code mapping.',
              file=sys.stderr)
        print(f'  This unit is not yet in the ministry index. Metadata generated for',
              file=sys.stderr)
        print(f'  this unit may be rejected by the platform.', file=sys.stderr)
        sys.exit(1)

    if args.format == 'json':
        print(json.dumps(info, ensure_ascii=False, indent=2))
    else:
        for k, v in info.items():
            if v is not None:
                print(f'{k}={v}')


if __name__ == '__main__':
    main()
