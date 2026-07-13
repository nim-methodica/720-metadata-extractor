#!/usr/bin/env python3
"""
Look up the prerequisiteLearningObjective for a 720/methodica unit ID.

The rule (as established by the user): the prerequisite of unit N is unit N-1
in the sequential order of learning objectives (as maintained in the management
Excel file, extracted to references/learning-objectives.json).

Usage:
    python lookup_prerequisite.py <unit-id>

Prints the prerequisite ID to stdout, or nothing (blank line) if this is the
first unit.

Exits with 0 on success, 1 if the ID is not found.
"""

import sys
import io
import json
import argparse
from pathlib import Path

# Make url_builder importable from the same directory
sys.path.insert(0, str(Path(__file__).parent))
from url_builder import build_url

# UTF-8 stdout on Windows consoles
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    except Exception:
        pass


def load_objectives(json_path: Path):
    if not json_path.is_file():
        raise SystemExit(f'Missing objectives file: {json_path}')
    with json_path.open(encoding='utf-8') as f:
        return json.load(f)


def find_prerequisite(unit_id: str, objectives: dict) -> str:
    """
    Search both math and science lists for the given unit_id and return the
    prerequisite (the ID of the entry immediately before it, in order).

    Returns empty string if unit_id is the first entry in its subject list.
    Returns None if unit_id is not found at all.
    """
    for subject, entries in objectives.items():
        for i, entry in enumerate(entries):
            if entry['id'] == unit_id:
                if i == 0:
                    return ''
                return entries[i - 1]['id']
    return None


def main():
    ap = argparse.ArgumentParser(description='Look up prerequisiteLearningObjective for a 720 unit ID.')
    ap.add_argument('unit_id', help='Full unit ID like methodica-math-scale-01')
    ap.add_argument('--json', default=None, help='Path to learning-objectives.json (default: next to this script)')
    ap.add_argument('--short', action='store_true', help='Return the short ID instead of the canonical URL')
    args = ap.parse_args()

    if args.json:
        json_path = Path(args.json)
    else:
        json_path = Path(__file__).parent.parent / 'references' / 'learning-objectives.json'

    objectives = load_objectives(json_path)
    prereq = find_prerequisite(args.unit_id, objectives)

    if prereq is None:
        print(f'ERROR: unit ID "{args.unit_id}" not found in learning objectives list.', file=sys.stderr)
        print('       If this is a new unit, refresh references/learning-objectives.json from the management Excel.', file=sys.stderr)
        sys.exit(1)

    if prereq == '' or args.short:
        # first-in-subject → empty; or user explicitly asked for short form
        print(prereq)
    else:
        print(build_url(prereq, objectives))


if __name__ == '__main__':
    main()
