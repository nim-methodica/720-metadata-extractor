#!/usr/bin/env python3
"""
source_fingerprint.py — חותמת מקור ליחידה מופקת, כדי לזהות שהנגן השתנה אחרי חילוץ המטא-דאטה.

שימוש:
    python source_fingerprint.py stamp <unit-dir> <output-dir>   # כותב <output-dir>/source-fingerprint.json
    python source_fingerprint.py check <unit-dir> <output-dir>   # משווה; קוד יציאה 1 אם יש שינוי

מה נחתם: קובצי תוכן של היחידה (html/htm/js/css/json/xlf/xliff/md-לא) — לא נכללים: node_modules, .git,
תיקיות metadata*, screenshots, _test, docs, output-*, ומדיה (תמונות/וידאו/שמע). הסקריפט מדווח בלבד ולא משנה
את היחידה. הקובץ היחיד שנכתב הוא חותמת הפלט (ב-stamp).
"""
import datetime
import hashlib
import json
import os
import sys

EXTS = (".html", ".htm", ".js", ".css", ".json", ".xlf", ".xliff")
SKIP_DIRS = {"node_modules", ".git", "metadata", "metadata-new", "screenshots", "_test", "docs",
             "docs-and-tools", "translation", "translations", "__pycache__"}
NAME = "source-fingerprint.json"


def collect(unit_dir):
    out = {}
    for dp, dn, fs in os.walk(unit_dir):
        dn[:] = sorted(d for d in dn if d not in SKIP_DIRS and not d.startswith("output-"))
        for f in sorted(fs):
            if not f.lower().endswith(EXTS):
                continue
            path = os.path.join(dp, f)
            rel = os.path.relpath(path, unit_dir).replace(os.sep, "/")
            with open(path, "rb") as fh:
                data = fh.read()
            # נרמול סוף שורה כדי ש-CRLF/LF לא ייחשבו שינוי
            data = data.replace(b"\r\n", b"\n")
            out[rel] = hashlib.sha256(data).hexdigest()
    return out


def combined(files):
    h = hashlib.sha256()
    for k in sorted(files):
        h.update(k.encode("utf-8") + b"\0" + files[k].encode() + b"\n")
    return h.hexdigest()


def main(argv):
    if len(argv) != 4 or argv[1] not in ("stamp", "check"):
        print(__doc__)
        return 2
    mode, unit_dir, out_dir = argv[1], argv[2], argv[3]
    if not os.path.isdir(unit_dir):
        print(f"תיקיית היחידה לא קיימת: {unit_dir}")
        return 2
    files = collect(unit_dir)
    stamp_path = os.path.join(out_dir, NAME)
    if mode == "stamp":
        os.makedirs(out_dir, exist_ok=True)
        data = {"unitDir": os.path.basename(os.path.abspath(unit_dir)),
                "createdAt": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "combined": combined(files), "fileCount": len(files), "files": files}
        with open(stamp_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"נכתבה חותמת: {stamp_path} ({len(files)} קבצים)")
        return 0
    if not os.path.exists(stamp_path):
        print(f"אין חותמת ({stamp_path}). הרץ stamp בסוף ההפקה.")
        return 2
    old = json.load(open(stamp_path, encoding="utf-8"))
    ofiles = old.get("files", {})
    changed = sorted(k for k in files if k in ofiles and files[k] != ofiles[k])
    added = sorted(k for k in files if k not in ofiles)
    removed = sorted(k for k in ofiles if k not in files)
    if not (changed or added or removed):
        print(f"הנגן לא השתנה מאז {old.get('createdAt')}.")
        return 0
    print(f"הנגן השתנה מאז {old.get('createdAt')}:")
    for tag, lst in (("שונה", changed), ("נוסף", added), ("הוסר", removed)):
        for k in lst:
            print(f"  {tag}: {k}")
    print("יש לחלץ מחדש את הפריטים המושפעים לפני מסירה.")
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
