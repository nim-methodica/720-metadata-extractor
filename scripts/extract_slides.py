#!/usr/bin/env python3
"""
Extract slides from a 720/methodica PPTX script and build a slide→item mapping.

Usage:
    python extract_slides.py <script.pptx> <output-dir>

Produces two files in <output-dir>:
    slides.txt  — full text of each slide, one section per slide
    mapping.txt — tabular map: slide_num, item_id, preview text
"""

import sys
import io
import re
import os
import zipfile
import shutil
import tempfile
import argparse
from pathlib import Path

# Ensure stdout can print Hebrew + arrows on Windows consoles
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    except Exception:
        pass


def extract_texts(xml: str):
    """Extract <a:t>...</a:t> text runs, preserving order."""
    return re.findall(r'<a:t[^>]*>([^<]*)</a:t>', xml)


def find_item_id(combined: str):
    """
    Find a full item ID like `methodica-<subject>-<topic>-01-01-001`.
    Item IDs have 5+ dash-separated segments after `methodica-`.
    Components are just 4 segments (methodica-<subject>-<topic>-01-01).
    """
    m = re.search(r'(methodica-[\w-]+?-\d+-\d+-\d+)', combined)
    return m.group(1) if m else None


def find_component_id(combined: str, full_text: str):
    """
    Find a component ID `methodica-<subject>-<topic>-01-01` (4 segments).
    Return only if this slide is a component divider (contains 'רכיב').
    """
    if 'רכיב' not in full_text:
        return None
    m = re.search(r'(methodica-[\w-]+?-\d+-\d+)(?!-\d)', combined)
    return m.group(1) if m else None


def process_pptx(pptx_path: Path, out_dir: Path):
    if not pptx_path.is_file():
        raise SystemExit(f"File not found: {pptx_path}")
    out_dir.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        with zipfile.ZipFile(pptx_path, 'r') as z:
            z.extractall(tmp_path)

        slides_dir = tmp_path / 'ppt' / 'slides'
        if not slides_dir.is_dir():
            raise SystemExit(f"No ppt/slides in {pptx_path}")

        slide_files = sorted(
            [f for f in slides_dir.iterdir() if f.name.startswith('slide') and f.suffix == '.xml'],
            key=lambda f: int(re.search(r'slide(\d+)', f.name).group(1)),
        )

        entries = []
        for f in slide_files:
            n = int(re.search(r'slide(\d+)', f.name).group(1))
            xml = f.read_text(encoding='utf-8')
            texts = extract_texts(xml)
            combined_no_ws = ''.join(texts)  # for regex over IDs split across runs
            full_text = ' | '.join(t for t in texts if t.strip())

            item_id = find_item_id(combined_no_ws)
            marker = item_id
            if not marker:
                comp_id = find_component_id(combined_no_ws, full_text)
                if comp_id:
                    marker = f'HEADER:{comp_id}'
            entries.append((n, marker or '', full_text))

    # slides.txt — full text per slide
    slides_txt = out_dir / 'slides.txt'
    with slides_txt.open('w', encoding='utf-8', newline='\n') as fh:
        for n, marker, text in entries:
            fh.write(f'=== SLIDE {n} === [{marker}]\n{text}\n\n')

    # mapping.txt — compact table
    mapping_txt = out_dir / 'mapping.txt'
    with mapping_txt.open('w', encoding='utf-8', newline='\n') as fh:
        fh.write('slide\titem_id\tpreview\n')
        for n, marker, text in entries:
            fh.write(f'{n}\t{marker}\t{text[:150]}\n')

    # Summary to stdout
    total = len(entries)
    with_item = sum(1 for _, m, _ in entries if m and not m.startswith('HEADER'))
    headers = [(n, m) for n, m, _ in entries if m and m.startswith('HEADER')]
    unique_items = sorted({m for _, m, _ in entries if m and not m.startswith('HEADER')})

    print(f'Slides:       {total}')
    print(f'With item ID: {with_item}')
    print(f'Unique items: {len(unique_items)}')
    print(f'Components:   {len(headers)}')
    for n, m in headers:
        cid = m.replace('HEADER:', '')
        items_in = sum(1 for i in unique_items if i.startswith(cid + '-'))
        print(f'  slide {n:>3} → {cid} ({items_in} items)')
    print()
    print(f'Output:')
    print(f'  {slides_txt}')
    print(f'  {mapping_txt}')

    if with_item == 0:
        print()
        print('WARNING: No item IDs (מספר פריט) found. The script cannot be split')
        print('into items without them. Ask the user to add item numbers before')
        print('proceeding with metadata extraction.')


def main():
    ap = argparse.ArgumentParser(description='Extract 720 script slides + item mapping.')
    ap.add_argument('pptx', help='Path to 720 script .pptx file')
    ap.add_argument('outdir', help='Output directory (created if missing)')
    args = ap.parse_args()
    process_pptx(Path(args.pptx), Path(args.outdir))


if __name__ == '__main__':
    main()
