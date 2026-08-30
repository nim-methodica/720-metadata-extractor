#!/usr/bin/env python3
"""
Extract slides from a STEM לומדה built with Articulate Storyline (HTML5 export)
and build a slide-to-item mapping — the Storyline equivalent of extract_slides.py.

Unlike a 720 PPTX script, a Storyline STEM unit has no local file: it's a live
web app. This script fetches the internal data files the Storyline player
itself loads (html5/data/js/data.js for the slide manifest, then one JS file
per slide) and pulls out every embedded "text":"..." string — the same text a
learner actually sees, including labels/answers that never show up in the
generic accessibility layer (round choice buttons show up there only as
"כפתור בחירה עגול", with no indication of which label they carry).

Usage:
    python extract_storyline_slides.py <story.html-url> <output-dir>

Produces two files in <output-dir>:
    slides.txt  — full text of each slide, one section per slide
    mapping.txt — tabular map: slide_num, slide_id, preview text

Note on item boundaries: a standard 720 PPTX has explicit "מספר פריט" tags.
A STEM Storyline unit does not — the whole לומדה is unit + a single component,
and item boundaries are a judgment call (by convention: one Storyline slide =
one item, unless the unit's own structure says otherwise). This script does
NOT try to guess item numbering; it only gives you the slide-level text so a
human (or the metadata-extractor flow) can decide item boundaries the way we
did for methodica-math-angles-ls01-00155.
"""

import sys
import io
import os
import re
import json
import argparse
import urllib.request

# Ensure stdout/stderr can print Hebrew + arrows on Windows consoles
for _stream_name in ("stdout", "stderr"):
    _stream = getattr(sys, _stream_name)
    if _stream.encoding and _stream.encoding.lower() != 'utf-8':
        try:
            setattr(sys, _stream_name, io.TextIOWrapper(_stream.buffer, encoding='utf-8'))
        except Exception:
            pass

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"

# Boilerplate text that recurs on nearly every slide (player chrome, feedback
# strings) — filtered out only for the mapping.txt preview, never dropped
# from slides.txt.
BOILERPLATE_PREFIXES = (
    "כפתור קדימה", "חדר עם לוקרים", "צדקתי", "עזרה", "נכון", "לא נכון",
    "זו אינה התשובה", "תוכלו ללחוץ", "צדקת!", "זו טעות", "התשובות הנכונות",
    "רקע צהוב", "רקע של בועית", "סגירה", "קו אופקי", "מאונך לרצפה", "בחרו",
    "כפתור בחירה עגול",
)


def fetch(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read().decode("utf-8", errors="replace")


_ID_RE = re.compile(r'"id":"([^"]+)"')
_TEXT_RE = re.compile(r'"text":"((?:\\.|[^"\\])*)"')

# Deliberately NOT doing a full json.loads() of the globalProvideData blob.
# It looks like plain JSON (single-quoted JS wrapper around a JSON object),
# but at least one field in data.js (a slide "title" carrying raw HTML with
# a doubly-escaped style="..." attribute) breaks a strict parse — the export
# pipeline escapes that one field inconsistently with the rest of the file.
# Regex-scanning for the specific keys we need ("id", "text") sidesteps that
# entirely and is what actually worked end-to-end when this was first done
# by hand for methodica-math-angles-ls01-00155.


def extract_texts(raw: str):
    """
    Pull every "text":"..." value out of a slide's raw JS payload, decoding
    standard JSON escapes (\\n, \\", \\\\, \\uXXXX) plus the JS-only \\'
    apostrophe escape described in parse_global_provide_data.
    """
    texts = []
    for m in _TEXT_RE.finditer(raw):
        val = m.group(1).replace("\\'", "'")
        try:
            val = json.loads('"' + val + '"')
        except (json.JSONDecodeError, ValueError):
            pass  # keep raw value rather than dropping it
        texts.append(val)
    return texts


def get_slide_ids(base_url: str):
    data_js = fetch(base_url + "html5/data/js/data.js")
    seen = set()
    ordered = []
    for m in _ID_RE.finditer(data_js):
        sid = m.group(1)
        if "." not in sid or sid.startswith("PromptScene") or sid.startswith("_player"):
            continue
        if sid in seen:
            continue
        seen.add(sid)
        leaf = sid.rsplit(".", 1)[-1]
        ordered.append(leaf)
    return ordered


def preview_text(texts, max_len=60):
    for t in texts:
        t = t.strip()
        if not t:
            continue
        if any(t.startswith(p) for p in BOILERPLATE_PREFIXES):
            continue
        if len(t) < 3:
            continue
        return (t[:max_len] + "…") if len(t) > max_len else t
    return "(ללא טקסט תיאורי — כנראה שקף אינטראקציה/תמונה בלבד)"


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("story_url", help="URL of the לומדה's story.html")
    ap.add_argument("output_dir")
    args = ap.parse_args()

    if not args.story_url.rstrip("/").endswith("story.html"):
        print("אזהרה: הקישור לא מסתיים ב-story.html — ודא שזה הקישור הנכון.", file=sys.stderr)

    base_url = args.story_url[: args.story_url.rfind("story.html")]
    os.makedirs(args.output_dir, exist_ok=True)

    print(f"מושך את מפת השקפים מ-{base_url}html5/data/js/data.js ...")
    slide_ids = get_slide_ids(base_url)
    print(f"נמצאו {len(slide_ids)} שקפים.")

    slides_path = os.path.join(args.output_dir, "slides.txt")
    mapping_path = os.path.join(args.output_dir, "mapping.txt")

    with open(slides_path, "w", encoding="utf-8") as slides_f, \
         open(mapping_path, "w", encoding="utf-8") as mapping_f:

        mapping_f.write("slide_num\tslide_id\tpreview\n")

        for i, sid in enumerate(slide_ids, start=1):
            slide_url = f"{base_url}html5/data/js/{sid}.js"
            try:
                raw = fetch(slide_url)
            except Exception as e:
                print(f"  שקף {i} ({sid}): שגיאת רשת — {e}", file=sys.stderr)
                slides_f.write(f"=== שקף {i} ({sid}) ===\n[שגיאת רשת בעת המשיכה: {e}]\n\n")
                mapping_f.write(f"{i}\t{sid}\t[שגיאת רשת]\n")
                continue

            texts = extract_texts(raw)
            slides_f.write(f"=== שקף {i} ({sid}) ===\n")
            for t in texts:
                slides_f.write(t + "\n")
            slides_f.write("\n")

            mapping_f.write(f"{i}\t{sid}\t{preview_text(texts)}\n")
            print(f"  שקף {i}/{len(slide_ids)} ({sid}): {len(texts)} מחרוזות טקסט")

    print(f"\nנכתב: {slides_path}")
    print(f"נכתב: {mapping_path}")
    print(f"\nסה\"כ שקפים: {len(slide_ids)}")
    print("שים לב: כל שקף = מועמד לפריט אחד, אלא אם צוין אחרת (אין תיוג 'מספר פריט' ביחידות STEM).")


if __name__ == "__main__":
    main()
