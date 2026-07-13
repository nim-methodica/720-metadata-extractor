#!/usr/bin/env python3
"""
Build canonical methodica 720 URLs from short IDs.

URL structure (per methodica ministry-of-education spec):
    https://lomdot.education.gov.il/metodica/720active/<subject>/<topic>/<unit-num>/[<component-id>/[<item-id>/]]

Examples:
    methodica-math-scale-01                    -> .../math/scale/01/
    methodica-science-mass-measure-01          -> .../science/mass-measure/01/
    methodica-science-mass-measure-01-01       -> .../science/mass-measure/01/methodica-science-mass-measure-01-01/
    methodica-science-mass-measure-01-01-001   -> .../science/mass-measure/01/methodica-science-mass-measure-01-01/methodica-science-mass-measure-01-01-001/
    methodica-character-materials-01           -> .../science/character-materials/01/  (subject inferred from learning-objectives.json)

Usage (CLI):
    python url_builder.py <id>

Usage (module):
    from url_builder import build_url
    url = build_url("methodica-math-scale-01", objectives_dict)
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


BASE = 'https://lomdot.education.gov.il/metodica/720active'


def _parse_id(entity_id: str):
    """
    Split a methodica ID into (subject-hint, topic-parts, numeric-tail).

    Numeric tail = trailing dash-separated integers. First numeric is the unit
    number; subsequent numbers are component/item.
    """
    if not entity_id.startswith('methodica-'):
        raise ValueError(f'Not a methodica ID: {entity_id!r}')
    parts = entity_id.split('-')[1:]  # drop 'methodica'

    # Collect trailing numeric parts
    numeric_tail = []
    while parts and parts[-1].isdigit():
        numeric_tail.insert(0, parts.pop())

    if not numeric_tail:
        raise ValueError(f'ID has no numeric part: {entity_id!r}')
    if not parts:
        raise ValueError(f'ID has no topic part: {entity_id!r}')

    return parts, numeric_tail


def _detect_subject(topic_parts, numeric_tail, objectives):
    """
    Determine the subject (math/science) for the given topic.

    Some IDs have an explicit subject prefix (methodica-math-* / methodica-science-*).
    Others (e.g. methodica-character-materials-*) don't — fall back to a lookup
    in learning-objectives.json.
    """
    if topic_parts[0] in ('math', 'science'):
        return topic_parts[0], topic_parts[1:]

    # Reconstruct the unit ID (short form) to look up
    unit_id = 'methodica-' + '-'.join(topic_parts) + '-' + numeric_tail[0]
    for subject, entries in objectives.items():
        if any(e['id'] == unit_id for e in entries):
            return subject, topic_parts

    raise ValueError(
        f'Cannot determine subject for {unit_id!r}. '
        f'Add it to references/learning-objectives.json (run refresh_objectives.py).'
    )


def build_url(entity_id: str, objectives: dict) -> str:
    """
    Build the canonical URL for a unit, component, or item ID.

    - `entity_id`: full methodica ID (e.g. methodica-science-mass-measure-01-01-001)
    - `objectives`: dict loaded from learning-objectives.json
                    (used to detect subject for prefix-less IDs)

    Returns the URL with trailing slash.
    """
    topic_parts, numeric_tail = _parse_id(entity_id)
    subject, topic_parts = _detect_subject(topic_parts, numeric_tail, objectives)
    topic = '-'.join(topic_parts)
    unit_num = numeric_tail[0]

    url = f'{BASE}/{subject}/{topic}/{unit_num}/'

    # Component / item — nest full ID(s) under the unit path
    if len(numeric_tail) == 2:
        # component: unit-num/component-full-id/
        url += f'{entity_id}/'
    elif len(numeric_tail) == 3:
        # item: unit-num/component-full-id/item-full-id/
        # Reconstruct component ID by dropping the last numeric segment
        component_id = 'methodica-' + '-'.join(topic_parts) + '-' + '-'.join(numeric_tail[:2])
        # If the id had a subject prefix, add it back
        if subject in ('math', 'science') and not entity_id.startswith(f'methodica-{subject}'):
            pass  # subject wasn't in the original id, keep component_id as-is
        elif entity_id.startswith(f'methodica-{subject}'):
            component_id = f'methodica-{subject}-' + '-'.join(topic_parts) + '-' + '-'.join(numeric_tail[:2])
        url += f'{component_id}/{entity_id}/'
    elif len(numeric_tail) > 3:
        raise ValueError(f'ID has too many numeric parts: {entity_id!r}')

    return url


def load_objectives(path: Path = None):
    if path is None:
        path = Path(__file__).parent.parent / 'references' / 'learning-objectives.json'
    with open(path, encoding='utf-8') as f:
        return json.load(f)


def main():
    ap = argparse.ArgumentParser(description='Build canonical 720 URL from a methodica ID.')
    ap.add_argument('entity_id', help='Full ID, e.g. methodica-science-mass-measure-01-01-001')
    ap.add_argument('--json', default=None, help='Path to learning-objectives.json')
    args = ap.parse_args()

    objectives = load_objectives(Path(args.json) if args.json else None)
    print(build_url(args.entity_id, objectives))


if __name__ == '__main__':
    main()
