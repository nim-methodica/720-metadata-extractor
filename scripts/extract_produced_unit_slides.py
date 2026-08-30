#!/usr/bin/env python3
"""
Extract screen text from a locally-built, already-produced 720 learning-unit
SPA (index.html + registry.js + script.js sitting in a project folder — the
built unit itself, not a script for it) and build a screen mapping — the
"produced unit" equivalent of extract_slides.py (PPTX) and
extract_storyline_slides.py (live Articulate Storyline).

Usage:
    python extract_produced_unit_slides.py <project-dir> <output-dir>

<project-dir> must contain index.html at its root; registry.js is optional
(used when present to get each screen's title/type/status).

Produces two files in <output-dir>:
    slides.txt  — full visible text of each implemented screen, one section each
    mapping.txt — tabular map: screen_id, type, preview

Like a Storyline export (and unlike a PPTX script), a produced unit has no
"מספר פריט" tag anywhere in its code. This script deliberately does NOT try
to guess item boundaries — see references/conventions.md, section "יחידות
720 מופקות", for the rule (an item follows the ORIGINAL approved script's
numbered question grouping, not necessarily the built unit's own sequential
on-screen renumbering, and not necessarily one item per <section>).

What this script does NOT do, by design:
  - It does not read script.js. Correct answers and dynamic feedback/hint
    strings live in script.js's own constants/validation logic (e.g.
    SC04_CORRECT = 'c'), not in the static HTML — grep script.js separately.
  - It does not split a merged screen (e.g. one <section> embedding several
    independently-graded sub-questions) into separate entries. Their nested
    headings/ids still show up in the extracted text — read it to spot them.
  - It does not decide item boundaries.
"""

import sys
import io
import re
import argparse
from pathlib import Path

for _stream_name in ("stdout", "stderr"):
    _stream = getattr(sys, _stream_name)
    if _stream.encoding and _stream.encoding.lower() != 'utf-8':
        try:
            setattr(sys, _stream_name, io.TextIOWrapper(_stream.buffer, encoding='utf-8'))
        except Exception:
            pass

_REGISTRY_ENTRY_RE = re.compile(
    r"\{\s*id:\s*'([^']+)'\s*,\s*title:\s*'((?:\\.|[^'\\])*)'\s*,\s*type:\s*'((?:\\.|[^'\\])*)'\s*,\s*status:\s*'([^']+)'\s*\}"
)

_TAG_RE = re.compile(r'<[^>]+>')
_SCRIPT_STYLE_RE = re.compile(r'<(script|style)\b[^>]*>.*?</\1>', re.DOTALL | re.IGNORECASE)
_BLOCK_TAG_RE = re.compile(r'<(p|div|section|h[1-6]|li|br|tr)\b[^>]*>', re.IGNORECASE)
_WS_RE = re.compile(r'[ \t\r\f\v]+')

_ENTITIES = {
    '&nbsp;': ' ', '&amp;': '&', '&lt;': '<', '&gt;': '>', '&quot;': '"',
    '&#39;': "'", '&rsquo;': '\u2019', '&lsquo;': '\u2018', '&mdash;': '\u2014', '&ndash;': '\u2013',
}


def _decode_entities(text: str) -> str:
    for ent, ch in _ENTITIES.items():
        text = text.replace(ent, ch)
    return re.sub(r'&#(\d+);', lambda m: chr(int(m.group(1))), text)


def strip_html(fragment: str) -> str:
    """
    Turn an HTML fragment into plain visible-ish text: drop script/style,
    turn block-level tags into line breaks (so elements don't run together),
    decode entities, collapse blank lines. Not a full HTML parser — tuned
    for hand-authored 720 produced-unit markup (semantic elements, no
    exotic nesting), same trade-off extract_storyline_slides.py makes with
    regex over a full JS parse instead of a proper one.
    """
    fragment = _SCRIPT_STYLE_RE.sub('\n', fragment)
    fragment = _BLOCK_TAG_RE.sub('\n', fragment)
    fragment = _TAG_RE.sub('', fragment)
    fragment = _decode_entities(fragment)
    fragment = _WS_RE.sub(' ', fragment)
    lines = [ln.strip() for ln in fragment.split('\n')]
    return '\n'.join(ln for ln in lines if ln)


def parse_registry(registry_js: str):
    """Extract SCREEN_REGISTRY entries as (id, title, type, status) tuples, in source order."""
    entries = []
    for m in _REGISTRY_ENTRY_RE.finditer(registry_js):
        sid, title, typ, status = m.groups()
        entries.append((sid, title.replace("\\'", "'"), typ.replace("\\'", "'"), status))
    return entries


def find_section(html: str, section_id: str):
    """
    Return the inner content of <section id="{section_id}" ...>...</section>.
    Assumes no <section> nests inside another (true of every produced unit
    seen so far — sub-question groupings are <div>s) — so a simple search
    for the next closing tag is enough; no depth balancing needed.
    """
    open_re = re.compile(r'<section\b[^>]*\bid="' + re.escape(section_id) + r'"[^>]*>')
    m = open_re.search(html)
    if not m:
        return None
    close_m = re.search(r'</section>', html[m.end():])
    if not close_m:
        return None
    return html[m.end():m.end() + close_m.start()]


_FALLBACK_SECTION_RE = re.compile(r'<section\b[^>]*\bid="([^"]+)"')


def discover_screens_without_registry(html: str):
    """Fallback when no registry.js exists: scan index.html directly for <section id="..."> screens."""
    seen = []
    for m in _FALLBACK_SECTION_RE.finditer(html):
        sid = m.group(1)
        if sid not in seen:
            seen.append(sid)
    return [(sid, '', 'unknown', 'implemented') for sid in seen]


def process(project_dir: Path, out_dir: Path):
    index_path = project_dir / 'index.html'
    if not index_path.is_file():
        raise SystemExit(f'index.html not found in {project_dir}')
    html = index_path.read_text(encoding='utf-8')

    registry_path = project_dir / 'registry.js'
    if registry_path.is_file():
        entries = parse_registry(registry_path.read_text(encoding='utf-8'))
        if not entries:
            print('WARNING: registry.js found but no SCREEN_REGISTRY entries matched the '
                  'expected {id, title, type, status} shape — falling back to scanning index.html directly.',
                  file=sys.stderr)
            entries = discover_screens_without_registry(html)
    else:
        print('No registry.js found — scanning index.html directly for <section id="..."> screens.')
        entries = discover_screens_without_registry(html)

    out_dir.mkdir(parents=True, exist_ok=True)
    slides_path = out_dir / 'slides.txt'
    mapping_path = out_dir / 'mapping.txt'

    results = []
    for sid, title, typ, status in entries:
        if status != 'implemented':
            continue
        section_html = find_section(html, sid)
        if section_html is None:
            print(f'  WARNING: {sid} is marked implemented but no matching <section id="{sid}"> '
                  f'found in index.html — skipping.', file=sys.stderr)
            continue
        text = strip_html(section_html)
        results.append((sid, title, typ, text))

    with slides_path.open('w', encoding='utf-8', newline='\n') as fh:
        for sid, title, typ, text in results:
            header = f'=== SCREEN {sid} === [{typ}]'
            if title:
                header += f' — {title}'
            fh.write(header + '\n' + text + '\n\n')

    with mapping_path.open('w', encoding='utf-8', newline='\n') as fh:
        fh.write('screen_id\ttype\tpreview\n')
        for sid, title, typ, text in results:
            preview = text.replace('\n', ' | ')[:150]
            fh.write(f'{sid}\t{typ}\t{preview}\n')

    print(f'Screens found (implemented): {len(results)}')
    print()
    print('Output:')
    print(f'  {slides_path}')
    print(f'  {mapping_path}')
    print()
    print('NOTE: this script does not read script.js (correct answers / feedback strings')
    print('live there, not in the HTML) and does not decide item boundaries — see')
    print('references/conventions.md, section "יחידות 720 מופקות", before building metadata.')


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('project_dir', help='Path to the produced unit\'s project folder (contains index.html)')
    ap.add_argument('outdir', help='Output directory (created if missing)')
    args = ap.parse_args()
    process(Path(args.project_dir), Path(args.outdir))


if __name__ == '__main__':
    main()
