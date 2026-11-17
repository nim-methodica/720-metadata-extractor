#!/usr/bin/env python3
"""
scan_source_text.py — סריקת קוד/תוכן של יחידה מופקת (index.html, script.js, js/, xlf) לפגמי הפקה.

מדווח בלבד (לא משנה קבצים). מיועד להפיק רשימה למפיקים לפני/אחרי הפקת מטא-דאטה.

שימוש:
    python scan_source_text.py <unit-dir> [--lang ar|he] [--json]

בדיקות:
    HID   תווי כיווניות/אפס-רוחב/NBSP (U+200B–200F, U+202A–202E, U+2066–2069, U+FEFF, U+00A0) בתוך טקסט
    MATH  תווים אלפביתיים-מתמטיים (U+1D400–1D7FF), למשל x נטוי
    HEB   (רק --lang ar) אותיות עבריות בקובצי HTML/JS/xlf-target של יחידה ערבית (לא כולל הערות קוד)
קוד יציאה: 0 = אין ממצאים, 1 = יש ממצאים.
"""
import collections
import json
import os
import re
import sys

EXTS = (".html", ".htm", ".js", ".json", ".xlf", ".xliff")
SKIP_DIRS = {"node_modules", ".git", "metadata", "metadata-new", "screenshots", "_test", "docs", "docs-and-tools"}
HIDDEN = re.compile("[​-‏‪-‮⁦-⁩﻿ ]")
MATH = re.compile("[\U0001D400-\U0001D7FF]")
HEB = re.compile("[֐-׿]")
CODE_COMMENT = re.compile(r"//[^\n]*|/\*.*?\*/|<!--.*?-->", re.S)
FILE_ATTR = re.compile(r"""(?:src|href|data-[\w-]*src)\s*=\s*(["'])[^"']*\1""")  # שמות קבצים בעברית אינם טקסט נראה
NAMES = {0x200b: "ZWSP", 0x200c: "ZWNJ", 0x200d: "ZWJ", 0x200e: "LRM", 0x200f: "RLM",
         0x202a: "LRE", 0x202b: "RLE", 0x202c: "PDF", 0x202d: "LRO", 0x202e: "RLO",
         0x2066: "LRI", 0x2067: "RLI", 0x2068: "FSI", 0x2069: "PDI", 0xfeff: "BOM", 0xa0: "NBSP"}


def main(argv):
    args = [a for a in argv[1:] if not a.startswith("--")]
    lang = None
    if "--lang" in argv:
        lang = argv[argv.index("--lang") + 1]
        args = [a for a in args if a != lang]
    if not args:
        print(__doc__)
        return 2
    root = args[0]
    findings = []
    per_file = collections.Counter()
    for dp, dn, fs in os.walk(root):
        dn[:] = [d for d in dn if d not in SKIP_DIRS]
        for f in fs:
            if not f.lower().endswith(EXTS):
                continue
            path = os.path.join(dp, f)
            try:
                text = open(path, encoding="utf-8").read()
            except Exception:
                continue
            rel = os.path.relpath(path, root)
            for lineno, line in enumerate(text.split("\n"), 1):
                for m in HIDDEN.finditer(line):
                    findings.append({"code": "HID", "file": rel, "line": lineno,
                                     "detail": f"U+{ord(m.group(0)):04X} {NAMES.get(ord(m.group(0)), '')}",
                                     "context": line[max(0, m.start() - 25):m.end() + 25].strip()})
                    per_file[rel] += 1
                if MATH.search(line):
                    m = MATH.search(line)
                    findings.append({"code": "MATH", "file": rel, "line": lineno,
                                     "detail": f"U+{ord(m.group(0)):04X}",
                                     "context": line[max(0, m.start() - 25):m.end() + 25].strip()})
                    per_file[rel] += 1
            if lang == "ar":
                if f.lower().endswith("_dev.html"):
                    continue  # קובצי פיתוח אינם נחשפים ללומד
                stripped = CODE_COMMENT.sub(lambda m: re.sub(r"[^\n]", " ", m.group(0)), text)
                stripped = FILE_ATTR.sub(lambda m: re.sub(r"[^\n]", " ", m.group(0)), stripped)
                for lineno, line in enumerate(stripped.split("\n"), 1):
                    if HEB.search(line):
                        m = HEB.search(line)
                        findings.append({"code": "HEB", "file": rel, "line": lineno, "detail": "עברית ביחידה ערבית",
                                         "context": line[max(0, m.start() - 25):m.end() + 40].strip()})
                        per_file[rel] += 1
    if "--json" in argv:
        print(json.dumps(findings, ensure_ascii=False, indent=2))
    else:
        by_code = collections.Counter(f["code"] for f in findings)
        for f in findings[:200]:
            print(f"{f['code']:4} {f['file']}:{f['line']} {f['detail']} | {f['context'][:70]}")
        if len(findings) > 200:
            print(f"... ועוד {len(findings) - 200} ממצאים (השתמש ב---json)")
        print("\nסיכום:", dict(by_code) or "אין ממצאים")
        if per_file:
            print("קבצים מושפעים:", len(per_file))
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
