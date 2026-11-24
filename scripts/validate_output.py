#!/usr/bin/env python3
"""
validate_output.py — בדיקת פלט של 720-metadata-extractor לפני מסירה.

מדווח בלבד (לעולם לא משנה קבצים). קורא תיקייה (רקורסיבית) עם קובצי JSON של
רכיבים (`subContent`) וקבצי יחידה (`*_unit.json`).

שימוש:
    python validate_output.py <dir> [<dir2> ...] [--json] [--only-errors]

קוד יציאה: 0 = אין ERROR, 1 = נמצאו ERROR, 2 = שגיאת שימוש.

חומרה:
    ERROR — מפר כלל מפורש בסקיל או באפשרות להתאים תשובה לנגן.
    WARN  — חשד שדורש שיפוט אנושי.

הבדיקות (מזהה → מקור הכלל):
    CT01  contentType מחוץ לרשימה הסגורה (standard.md)
    TM01  estimatedTimeInMinutes לא תואם לחישוב (conventions.md שדה 7; משימה מחוץ למחשב = 5)
    TF01  true-false שאינו ["true","false"] / ["true"|"false"]
    CH01  choice: תשובה נכונה שאינה בין האפשרויות
    MA01  matching: זוג תשובה נכונה שאינו בין source/target
    SE01  solved-exercise עם questions לא ריק
    PF01  performance: סכימה ישנה (steps) — נדחית ע"י הפלטפורמה — / שלב בלי stepId או response
    RS01  מחרוזת שמכילה מפריד שמור ([,] [.] [:]) בתשובה/stepId/response
    TX01  תווי כיווניות/רווח לא שבור/אפס-רוחב בתוך טקסט
    TX02  תווים אלפבתיים-מתמטיים (U+1D400–1D7FF), למשל x נטוי
    TX03  רווח בתחילת/סוף תשובה (answers/correctAnswers/stepId/response)
    TX04  גרשיים עבריים וגרשיים ASCII ב"ש"ח" באותה שאלה
    TX05  יחס עם רווחים סביב נקודתיים (a : b) בתשובה
    IB01  informationToBot חסר אחד מחמשת הסעיפים
    MS01  הנחיית ריבוי מסכים לא בנוסח המלא, או לא בתחילת השדה (לפני "מטרת הפריט")
    MS02  הנחיה בלי "מפת המסכים:" או להפך; מפה מחוץ ל"מידע נוסף" (WARN)
    MS03  מפת מסכים עם פחות מ-2 מסכים או מספור לא רציף מ-1
    MS04  פריט instruction שמזכיר כמה מסכים בלי הנחיה ומפה (WARN — מספר המסכים לא ידוע לסקריפט)
    ID01  מזהה רכיב/פריט שאינו URL מלא
    ID02  מספור פריטים לא רציף או order לא תואם סדר
    UN01  כותרת יחידה ארוכה מ-30 תווים
    DD01  שאלת performance/matching עם רשימות נפתחות שאין לה אפשרויות בשום שדה
    AR01  טקסט עברי בתוך שדה ערבי (title/questionText/answers/correctAnswers)
    AR02  חשד כתיב בערבית: מילה כפולה / "الال" / רווח חסר לפני לטינית / מקף אחרי و
    PR01  זוג עברית-ערבית: שדה מבנה שונה (order, isRequired, componentPurpose, ...)
    PR02  זוג עברית-ערבית: מספר פריטים/שאלות/סוג שאלה שונה
    PR03  זוג עברית-ערבית: informationToBot שונה (WARN — ייתכן עדכון עברי שלא הועתק)
"""
import json
import os
import re
import sys
import collections

CONTENT_TYPES = {
    "instruction", "practice", "project-or-inquiry-task", "game-educational",
    "text-reading", "simulation", "motivational", "solved-exercise", "summary",
}
STRUCT_FIELDS = (
    "order", "isRequired", "componentPurpose", "isAssessment",
    "recommendedAfterFail", "relativeDifficulty", "masteryLevel",
    "depthLevel", "cognitiveLevels", "estimatedTimeInMinutes",
)
IB_SECTIONS = (
    "מטרת הפריט", "מה התלמיד אמור להבין", "כיווני חשיבה",
    "טעויות נפוצות", "מידע נוסף",
)
# "משימה מחוץ למחשב" / "مهمّة ميدانية" = השם הנוכחי (2026-11-22); השמות הישנים נשארים לזיהוי פלט/תסריטים ישנים
CLASS_TASK_TITLE = re.compile(r"משימה מחוץ למחשב|مهمّة ميدانية|مهمة ميدانية|משימת כיתה|משימה בכיתה|משימה בחצר|مهمة صفية|مهمّة صفية")

# פריטים מרובי מסכים (2026-11-24)
MS_DIRECTIVE = (
    "שים לב: הפריט הזה מורכב מכמה מסכים, ואין לך דרך לדעת באיזה מסך הלומד נמצא כרגע. "
    "התיאור שלהלן מפרט את כל המסכים בפריט. כשהלומד שואל על הפריט, נסה להבין מדבריו באיזה מסך הוא נמצא. "
    "אם זה לא ברור, שאל אותו שאלת הבהרה קצרה (למשל \"מה כתוב לך על המסך עכשיו?\" או \"איזו שאלה מופיעה מולך?\"). "
    "אחרי שזיהית את המסך, היעזר בתיאור שלו כדי לעזור ללומד כמה שיותר."
)
MS_DIRECTIVE_KEY = "הפריט הזה מורכב מכמה מסכים"
MS_MAP_HEADER = "מפת המסכים:"
MS_ENTRY = re.compile(r"(?:^|\n)\s*מסך\s+(\d+)\s*[—–-]")
MS_SUSPECT = re.compile(r"מסך\s*2\b|\d+\s+מסכים|כמה מסכים|במסך השני|במסך הבא")

HIDDEN = re.compile("[​-‏‪-‮⁠-⁤⁦-⁩﻿ ]")
MATH_ALNUM = re.compile("[\U0001D400-\U0001D7FF]")
HEB = re.compile("[֐-׿]")
ARB = re.compile("[؀-ۿ]")
SHEKEL_HE = re.compile(r'ש״ח')
SHEKEL_ASCII = re.compile(r'ש"ח')
RATIO_SPACED = re.compile(r"\d\s+:\s+\d|\w\s+:\s+\d|\d\s+:\s+\w")


class Report:
    def __init__(self):
        self.items = []

    def add(self, sev, code, where, msg):
        self.items.append({"severity": sev, "code": code, "where": where, "message": msg})


def load_json(path):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def walk_strings(obj, path=""):
    """yield (path, string) for every string in a JSON value."""
    if isinstance(obj, str):
        yield path, obj
    elif isinstance(obj, dict):
        for k, v in obj.items():
            yield from walk_strings(v, f"{path}.{k}" if path else k)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from walk_strings(v, f"{path}[{i}]")


def flat(v):
    """שטח תשובות חלופיות מקוננות ([[...],[...]]) לרשימה אחת."""
    out = []
    for x in v:
        if isinstance(x, list):
            out.extend(flat(x))
        else:
            out.append(x)
    return out


def answer_strings(q):
    """strings that a student's response must equal (answers / correctAnswers / step values)."""
    out = []
    for key in ("answers", "correctAnswers"):
        v = q.get(key)
        if isinstance(v, list):
            for x in flat(v):
                if isinstance(x, str):
                    out.append((key, x))
                elif isinstance(x, dict):
                    for kk in ("source", "target", "stepId", "response"):
                        if isinstance(x.get(kk), str):
                            out.append((f"{key}.{kk}", x[kk]))
        elif isinstance(v, dict):
            for kk, lst in v.items():
                if isinstance(lst, list):
                    out.extend((f"{key}.{kk}", s) for s in lst if isinstance(s, str))
    return out


def comp_expected_minutes(items):
    total = 0
    for it in items:
        qs = it.get("questions") or []
        is_task = it.get("contentType") == "project-or-inquiry-task" or bool(
            CLASS_TASK_TITLE.search(it.get("title") or ""))
        if is_task and not qs:
            total += 5
        elif qs:
            total += 2 * len(qs)
        else:
            total += 1
    return total


def check_multi_screen(iname, ct, ib, rep):
    """MS01-MS04: הנחיית ריבוי מסכים + מפת מסכים (conventions.md, "פריטים מרובי מסכים", 2026-11-24)."""
    has_directive = MS_DIRECTIVE_KEY in ib
    map_pos = ib.find(MS_MAP_HEADER)
    entries = [int(n) for n in MS_ENTRY.findall(ib[map_pos:])] if map_pos >= 0 else []
    if has_directive and MS_DIRECTIVE not in ib:
        rep.add("ERROR", "MS01", iname, "הנחיית ריבוי המסכים לא בנוסח המלא מילה במילה")
    if has_directive:
        first_section = ib.find(IB_SECTIONS[0])
        if first_section >= 0 and ib.find(MS_DIRECTIVE_KEY) > first_section:
            rep.add("ERROR", "MS01", iname, "הנחיית ריבוי המסכים מופיעה אחרי 'מטרת הפריט' (צריכה להיות בתחילת השדה)")
    if has_directive and map_pos < 0:
        rep.add("ERROR", "MS02", iname, "יש הנחיית ריבוי מסכים אבל אין 'מפת המסכים:'")
    if map_pos >= 0:
        if not has_directive:
            rep.add("ERROR", "MS02", iname, "יש 'מפת המסכים:' אבל חסרה הנחיית ריבוי המסכים בתחילת השדה")
        extra = ib.find(IB_SECTIONS[4])
        if extra < 0 or map_pos < extra:
            rep.add("WARN", "MS02", iname, "'מפת המסכים:' לא נמצאת בתוך סעיף 'מידע נוסף'")
        if len(entries) < 2:
            rep.add("ERROR", "MS03", iname, f"במפת המסכים {len(entries)} מסכים (הכלל חל מ-2 מסכים ומעלה)")
        elif entries != list(range(1, len(entries) + 1)):
            rep.add("ERROR", "MS03", iname, f"מספור המסכים במפה לא רציף מ-1: {entries}")
    elif not has_directive and ct == "instruction" and MS_SUSPECT.search(ib):
        rep.add("WARN", "MS04", iname, "פריט הקנייה שמזכיר כמה מסכים בלי הנחיה ומפת מסכים (אם 2+ מסכים — חובה לפריט חדש)")


def is_arabic_file(d):
    langs = d.get("languages") or []
    return "Arabic" in langs


def check_component(path, d, rep):
    name = os.path.basename(path)
    arabic = is_arabic_file(d)
    items = d.get("subContent") or []

    # ID01 + ID02
    cid = d.get("id")
    if not (isinstance(cid, str) and cid.startswith("http")):
        rep.add("ERROR", "ID01", name, f"מזהה הרכיב אינו URL מלא: {cid!r}")
    nums = []
    for it in items:
        iid = it.get("id")
        if not (isinstance(iid, str) and iid.startswith("http")):
            rep.add("ERROR", "ID01", name, f"מזהה פריט אינו URL מלא: {iid!r}")
        m = re.search(r"-(\d{3})/?(?:index\.html)?$", iid or "")
        nums.append(int(m.group(1)) if m else None)
    good = [n for n in nums if n is not None]
    if good and good != list(range(good[0], good[0] + len(good))):
        rep.add("ERROR", "ID02", name, f"מספור פריטים לא רציף: {good}")
    elif good and good[0] != 1:
        rep.add("WARN", "ID02", name, f"המספור אינו מתחיל ב-001: {good[:5]}")

    # TM01
    exp = comp_expected_minutes(items)
    got = d.get("estimatedTimeInMinutes")
    if got != exp:
        rep.add("ERROR", "TM01", name, f"estimatedTimeInMinutes={got}, מחושב={exp}")

    # IB01 / CT01 / per question
    for it in items:
        iname = f"{name}:{str(it.get('id'))[-12:]}"
        ct = it.get("contentType")
        if ct not in CONTENT_TYPES:
            rep.add("ERROR", "CT01", iname, f"contentType לא תקני: {ct!r}")
        ib = it.get("informationToBot") or ""
        missing = [s for s in IB_SECTIONS if s not in ib]
        if missing:
            rep.add("ERROR", "IB01", iname, "חסרים סעיפי informationToBot: " + ", ".join(missing))
        check_multi_screen(iname, ct, ib, rep)
        qs = it.get("questions") or []
        if ct == "solved-exercise" and qs:
            rep.add("ERROR", "SE01", iname, f"תרגול מונחה עם {len(qs)} שאלות (צריך questions=[])")
        has_dropdown_hint = ("רשימ" in ib) or ("נפתח" in ib) or ("אפשרויות" in ib) or ("خيارات" in ib)
        for q in qs:
            qname = f"{iname}/{str(q.get('questionId'))[-8:]}"
            qt = q.get("questionType")
            a, c = q.get("answers"), q.get("correctAnswers")
            if qt == "true-false":
                if a != ["true", "false"] or c not in (["true"], ["false"]):
                    rep.add("ERROR", "TF01", qname, f"true-false לא תקני: answers={a!r} correctAnswers={c!r}")
            if qt == "choice" and isinstance(a, list) and isinstance(c, list):
                for x in c:
                    if x not in a and "{" not in str(x):  # תבניות עם {placeholder} (יחידות עם תוכן דינמי) נבדקות ידנית
                        rep.add("ERROR", "CH01", qname, f"תשובה נכונה לא בין האפשרויות: {str(x)[:50]!r}")
            if qt == "matching" and isinstance(a, dict) and isinstance(c, list):
                src, tgt = a.get("source") or [], a.get("target") or []
                for pair in flat(c):
                    if isinstance(pair, dict):
                        if pair.get("source") not in src or pair.get("target") not in tgt:
                            rep.add("ERROR", "MA01", qname, f"זוג נכון מחוץ לרשימות: {str(pair)[:80]}")
            if qt == "performance":
                if q.get("steps") and not (isinstance(c, list) and c and isinstance(c[0], dict) and "stepId" in c[0]):
                    rep.add("ERROR", "PF01", qname, "סכימת performance ישנה (steps) — Kata דוחה אותה ב-HTTP 422; הסכימה: correctAnswers=[{stepId,response}]")
                if isinstance(c, list):
                    for st in c:
                        if isinstance(st, dict) and ("stepId" not in st or "response" not in st):
                            rep.add("ERROR", "PF01", qname, f"שלב בלי stepId/response: {str(st)[:80]}")
                has_options = bool(a) or any("options" in (s if isinstance(s, dict) else {}) for s in (c or []))
                if not has_options and not has_dropdown_hint and qt in ("performance", "matching"):
                    rep.add("WARN", "DD01", qname, "אין אפשרויות בשדות ולא מוזכרות ב-informationToBot (אם יש רשימות נפתחות — חובה)")
            # text checks
            shek_he = shek_ascii = False
            for p, s in walk_strings(q):
                if HIDDEN.search(s):
                    rep.add("ERROR", "TX01", qname, f"תו נסתר/NBSP ב-{p}: {repr(s[:40])}")
                if MATH_ALNUM.search(s):
                    rep.add("ERROR", "TX02", qname, f"תו אלפבתי-מתמטי ב-{p}: {s[:40]!r}")
                shek_he |= bool(SHEKEL_HE.search(s))
                shek_ascii |= bool(SHEKEL_ASCII.search(s))
                if arabic and re.split(r"[.\[]", p)[0] in ("questionText", "answers", "correctAnswers") and HEB.search(s):
                    rep.add("ERROR", "AR01", qname, f"טקסט עברי בשדה ערבי {p}: {s[:50]!r}")
            for key, s in answer_strings(q):
                for tok in ("[,]", "[.]", "[:]"):
                    if tok in s:
                        rep.add("ERROR", "RS01", qname, f"מפריד שמור {tok} ב-{key}: {s[:40]!r}")
                if s != s.strip():
                    rep.add("ERROR", "TX03", qname, f"רווח בקצה ב-{key}: {s[:40]!r}")
                if RATIO_SPACED.search(s):
                    rep.add("WARN", "TX05", qname, f"יחס עם רווחים ב-{key}: {s[:40]!r}")
            if shek_he and shek_ascii:
                rep.add("WARN", "TX04", qname, 'גם ש״ח (גרשיים עבריים) וגם ש"ח (ASCII) באותה שאלה')
            if arabic:
                for p, s in walk_strings({"questionText": q.get("questionText"), "answers": a, "correctAnswers": c}):
                    check_arabic_text(qname, p, s, rep)

    # titles / bot: text hygiene on item titles too
    for it in items:
        for p, s in (("title", it.get("title") or ""),):
            if HIDDEN.search(s) or MATH_ALNUM.search(s):
                rep.add("ERROR", "TX01", f"{name}:{str(it.get('id'))[-12:]}", f"תו נסתר/מתמטי בכותרת: {s[:40]!r}")
            if arabic and HEB.search(s):
                rep.add("ERROR", "AR01", f"{name}:{str(it.get('id'))[-12:]}", f"טקסט עברי בכותרת ערבית: {s[:50]!r}")
    if arabic and HEB.search(d.get("title") or ""):
        rep.add("ERROR", "AR01", name, f"טקסט עברי בכותרת הרכיב: {d.get('title')!r}")


DUP_WORD = re.compile(r"(?<![\w])([؀-ۿ]{2,})\s+\1(?![\w])")
DOUBLE_AL = re.compile(r"\bالال")
LATIN_GLUE = re.compile(r"[؀-ۿ][A-Za-z]|[A-Za-z][؀-ۿ]")
WAW_DASH = re.compile(r"(?<![\w])[وبلك]-(?=[\w\d])")


def check_arabic_text(where, p, s, rep):
    if DUP_WORD.search(s):
        rep.add("WARN", "AR02", where, f"מילה כפולה ב-{p}: {DUP_WORD.search(s).group(0)!r}")
    if DOUBLE_AL.search(s):
        rep.add("WARN", "AR02", where, f"'الال' ב-{p}: {s[:50]!r}")
    if LATIN_GLUE.search(s):
        rep.add("WARN", "AR02", where, f"אות לטינית צמודה לערבית ב-{p}: {s[:50]!r}")
    if WAW_DASH.search(s):
        rep.add("WARN", "AR02", where, f"מקף אחרי אות חיבור/יחס ב-{p}: {s[:50]!r}")


def check_unit(path, d, rep):
    name = os.path.basename(path)
    title = d.get("title") or ""
    if len(title) > 30:
        rep.add("ERROR", "UN01", name, f"כותרת יחידה {len(title)} תווים (>30): {title!r}")
    if HIDDEN.search(title) or MATH_ALNUM.search(title) or title.count('"') % 2:
        rep.add("ERROR", "TX01", name, f"תו חריג/מרכאה בודדת בכותרת יחידה: {title!r}")


def norm_name(name):
    n = re.sub(r"^methodica-ar-", "methodica-", name)
    return n.replace("-arab-", "-")


def pair_checks(comps, rep):
    groups = collections.defaultdict(lambda: {"he": None, "ar": None})
    for path, d in comps:
        key = norm_name(os.path.basename(path))
        side = "ar" if is_arabic_file(d) else "he"
        cur = groups[key][side]
        if cur is None or os.path.getmtime(path) > os.path.getmtime(cur[0]):
            groups[key][side] = (path, d)
    for key, g in groups.items():
        if not (g["he"] and g["ar"]):
            continue
        (hp, h), (ap, a) = g["he"], g["ar"]
        name = os.path.basename(ap)
        for f in STRUCT_FIELDS:
            if f == "recommendedAfterFail":
                continue  # URL שונה בין השפות; נבדק בנפרד
            if a.get(f) != h.get(f):
                rep.add("ERROR", "PR01", name, f"{f}: ערבית={a.get(f)!r} עברית={h.get(f)!r}")
        if bool(a.get("recommendedAfterFail")) != bool(h.get("recommendedAfterFail")):
            rep.add("ERROR", "PR01", name, "recommendedAfterFail: אחד ריק ואחד לא")
        ai, hi = a.get("subContent") or [], h.get("subContent") or []
        if len(ai) != len(hi):
            rep.add("ERROR", "PR02", name, f"מספר פריטים: ערבית={len(ai)} עברית={len(hi)}")
            continue
        for x, y in zip(ai, hi):
            xi = str(x.get("id"))[-12:]
            for f in ("contentType", "mediaFormat"):
                if x.get(f) != y.get(f):
                    rep.add("ERROR", "PR01", f"{name}:{xi}", f"{f}: ערבית={x.get(f)!r} עברית={y.get(f)!r}")
            qa, qh = x.get("questions") or [], y.get("questions") or []
            if len(qa) != len(qh):
                rep.add("ERROR", "PR02", f"{name}:{xi}", f"מספר שאלות: ערבית={len(qa)} עברית={len(qh)}")
            else:
                for q1, q2 in zip(qa, qh):
                    if q1.get("questionType") != q2.get("questionType"):
                        rep.add("ERROR", "PR02", f"{name}:{xi}", f"questionType: ערבית={q1.get('questionType')} עברית={q2.get('questionType')}")
            if (x.get("informationToBot") or "").strip() != (y.get("informationToBot") or "").strip():
                rep.add("WARN", "PR03", f"{name}:{xi}", "informationToBot שונה מהעברית (הכלל: מועתק מילה במילה)")


def main(argv):
    args = [a for a in argv[1:] if not a.startswith("--")]
    flags = {a for a in argv[1:] if a.startswith("--")}
    if not args:
        print(__doc__)
        return 2
    rep = Report()
    comps = []
    n_units = 0
    for root in args:
        for dp, _dn, fs in os.walk(root):
            for f in sorted(fs):
                if not f.endswith(".json"):
                    continue
                path = os.path.join(dp, f)
                d = load_json(path)
                if not isinstance(d, dict):
                    continue
                if f.endswith("_unit.json"):
                    n_units += 1
                    check_unit(path, d, rep)
                elif "subContent" in d:
                    comps.append((path, d))
                    check_component(path, d, rep)
    pair_checks(comps, rep)

    items = rep.items
    if "--only-errors" in flags:
        items = [i for i in items if i["severity"] == "ERROR"]
    if "--json" in flags:
        print(json.dumps(items, ensure_ascii=False, indent=2))
    else:
        by = collections.Counter((i["severity"], i["code"]) for i in items)
        print(f"רכיבים שנסרקו: {len(comps)} | קבצי יחידה: {n_units}")
        for i in items:
            print(f"{i['severity']:5} {i['code']} {i['where']}: {i['message']}")
        print("\nסיכום:")
        for (sev, code), n in sorted(by.items()):
            print(f"  {sev:5} {code}: {n}")
        if not items:
            print("  הבדיקה עברה — אין סטיות.")
    return 1 if any(i["severity"] == "ERROR" for i in rep.items) else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
