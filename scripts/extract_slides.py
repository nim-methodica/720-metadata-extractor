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


def _fraction_repl(m):
    """Reconstruct a <m:f> (OOXML equation fraction) as a plain 'num/den' token."""
    frac_xml = m.group(0)
    num_m = re.search(r'<m:num>(.*?)</m:num>', frac_xml, re.DOTALL)
    den_m = re.search(r'<m:den>(.*?)</m:den>', frac_xml, re.DOTALL)
    num = ''.join(re.findall(r'<m:t[^>]*>([^<]*)</m:t>', num_m.group(1))) if num_m else ''
    den = ''.join(re.findall(r'<m:t[^>]*>([^<]*)</m:t>', den_m.group(1))) if den_m else ''
    return f'<a:t>{num}/{den}</a:t>'


def extract_texts(xml: str):
    """
    Extract <a:t>...</a:t> text runs, preserving order.

    Also handles inline OOXML equation objects (<m:oMath>, inserted via
    PowerPoint's native equation editor): fractions (<m:f>/<m:num>/<m:den>)
    are reconstructed as "num/den" tokens, and any other bare <m:t> runs
    (=, ≠, plain numbers/variables not inside a fraction) are captured too.
    Without this, equation-editor content is silently invisible — no
    placeholder, no warning, just missing numbers with nothing in slides.txt
    to suggest anything was dropped.
    """
    xml = re.sub(r'<m:f>.*?</m:f>', _fraction_repl, xml, flags=re.DOTALL)
    matches = re.findall(r'<a:t[^>]*>([^<]*)</a:t>|<m:t[^>]*>([^<]*)</m:t>', xml)
    return [a or m for a, m in matches]


def find_item_id(combined: str):
    """
    Find a full item ID like `methodica-<subject>-<topic>-01-01-001`.
    Item IDs have 5+ dash-separated segments after `methodica-`.
    Components are just 4 segments (methodica-<subject>-<topic>-01-01).
    """
    m = re.search(r'(methodica-[\w-]+?-\d+-\d+-\d+)', combined)
    return m.group(1) if m else None


def find_component_id(combined: str):
    """
    Find a component ID `methodica-<subject>-<topic>-01-01` (4 segments).
    Only called when the slide has no full item ID, so a bare 4-segment ID
    here is virtually always a component-divider slide. Do NOT require the
    word 'רכיב' — some scripts label dividers with the component's role
    instead (e.g. 'תרגול מתקדם', 'שאלת שיא') and never say 'רכיב' at all.
    """
    m = re.search(r'(methodica-[\w-]+?-\d+-\d+)(?!-\d)', combined)
    return m.group(1) if m else None


_DARK_HEX_THRESHOLD = 0x30  # treat as "black" if every RGB channel is this dark or darker


def is_divider_background(xml: str) -> bool:
    """
    720 scripts mark component-divider slides with a solid BLACK slide
    background (as opposed to the normal white/theme background every
    content slide inherits) — this is a reliable structural signal,
    independent of whatever text (if any) is on the slide. Recognizes the
    theme's dark text color (<a:schemeClr val="tx1"/>, almost universally
    black in Office themes) as well as a literal near-black <a:srgbClr>.
    Do NOT match other background overrides (e.g. bg1/white cover slides)
    — those are unrelated one-off slide styling, not dividers.
    """
    bg_m = re.search(r'<p:bg>.*?</p:bg>', xml, re.DOTALL)
    if not bg_m:
        return False
    bg_xml = bg_m.group(0)
    if re.search(r'<a:schemeClr val="tx1"\s*/?>', bg_xml):
        return True
    hex_m = re.search(r'<a:srgbClr val="([0-9A-Fa-f]{6})"', bg_xml)
    if hex_m:
        r, g, b = (int(hex_m.group(1)[i:i + 2], 16) for i in (0, 2, 4))
        return max(r, g, b) <= _DARK_HEX_THRESHOLD
    return False


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
                comp_id = find_component_id(combined_no_ws)
                if comp_id:
                    marker = f'HEADER:{comp_id}'
                elif is_divider_background(xml):
                    # Black-background divider slide, but no component ID
                    # found as text (e.g. a purely graphical divider) — flag
                    # it loudly instead of silently treating it as untagged
                    # content, so a human can assign the component number.
                    marker = 'HEADER:UNKNOWN'
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

    unresolved = [n for n, m in headers if m == 'HEADER:UNKNOWN']

    print(f'Slides:       {total}')
    print(f'With item ID: {with_item}')
    print(f'Unique items: {len(unique_items)}')
    print(f'Components:   {len(headers) - len(unresolved)}')
    for n, m in headers:
        if m == 'HEADER:UNKNOWN':
            continue
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

    if unresolved:
        print()
        print(f'WARNING: {len(unresolved)} black-background divider slide(s) found with')
        print('no component ID as text — cannot tell which component they start.')
        print('Inspect these slides manually before trusting the component count above:')
        for n in unresolved:
            print(f'  slide {n}')


def main():
    ap = argparse.ArgumentParser(description='Extract 720 script slides + item mapping.')
    ap.add_argument('pptx', help='Path to 720 script .pptx file')
    ap.add_argument('outdir', help='Output directory (created if missing)')
    args = ap.parse_args()
    process_pptx(Path(args.pptx), Path(args.outdir))


if __name__ == '__main__':
    main()
