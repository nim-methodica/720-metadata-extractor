#!/usr/bin/env python3
"""בדיקות עצמאיות ל-validate_output.py: פלט נקי עובר; כל פגם מושתל מזוהה בקוד הנכון."""
import copy
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
VALIDATOR = os.path.join(HERE, "validate_output.py")
BASE = "https://lomdot.education.gov.il/metodica/720active/math/ratio/01/methodica-math-ratio-01/methodica-math-ratio-01-01/"
BOT = ("מטרת הפריט: x. מה התלמיד אמור להבין/לתרגל: x. כיווני חשיבה ואסטרטגיות: x. "
       "טעויות נפוצות: x. מידע נוסף: x.")


def item(n, ct="practice", questions=None, title="תרגול 1: יחס"):
    return {"id": f"{BASE}methodica-math-ratio-01-01-{n:03d}/", "title": title,
            "informationToBot": BOT, "contentType": ct, "mediaFormat": "interactive-content",
            "questions": questions if questions is not None else []}


def q(qt="choice", a=None, c=None, text="שאלה?"):
    return {"questionId": BASE + "q1", "questionType": qt, "questionText": text,
            "answers": a if a is not None else [], "correctAnswers": c if c is not None else []}


def component(items, langs=("Hebrew",), minutes=None, title="הבנייה"):
    exp = 0
    for it in items:
        qs = it["questions"]
        if it["contentType"] == "project-or-inquiry-task" and not qs:
            exp += 5
        elif qs:
            exp += 2 * len(qs)
        else:
            exp += 1
    return {"id": BASE, "title": title, "learningUnitId": "methodica-math-ratio-01",
            "componentPurpose": "practice", "isAssessment": False, "recommendedAfterFail": [],
            "isRequired": True, "relativeDifficulty": 3, "masteryLevel": None, "order": 1,
            "depthLevel": "core-curriculum-basic", "cognitiveLevels": ["applying"],
            "languages": list(langs), "skills": [],
            "estimatedTimeInMinutes": exp if minutes is None else minutes, "subContent": items}


def good_component():
    return component([
        item(1, "motivational"),
        item(2, "practice", [q("choice", ["א", "ב"], ["א"]), q("true-false", ["true", "false"], ["true"])]),
        item(3, "project-or-inquiry-task", [], "משימה מחוץ למחשב: מדידה"),
    ])


def run(files):
    with tempfile.TemporaryDirectory() as tmp:
        for name, data in files.items():
            with open(os.path.join(tmp, name), "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False)
        r = subprocess.run([sys.executable, "-X", "utf8", VALIDATOR, tmp, "--json"],
                           capture_output=True, text=True, encoding="utf-8")
        return r.returncode, json.loads(r.stdout or "[]")


def codes(findings):
    return {f["code"] for f in findings}


def mutate(fn):
    c = good_component()
    fn(c)
    return {"c.json": c}


FAILS = []


def expect(label, files, want_code=None, want_clean=False):
    rc, found = run(files)
    got = codes(found)
    ok = (rc == 0 and not found) if want_clean else (want_code in got)
    print(("PASS " if ok else "FAIL ") + label + ("" if ok else f"  (got {sorted(got)} rc={rc})"))
    if not ok:
        FAILS.append(label)


def main():
    expect("נקי עובר", {"c.json": good_component()}, want_clean=True)
    expect("משימה מחוץ למחשב = 5 דקות (נכון) עובר", {"c.json": component([item(1, "project-or-inquiry-task", [], "משימה מחוץ למחשב")])}, want_clean=True)
    expect("TM01 משימה מחוץ למחשב = 1 דקה (כלל ישן)", mutate(lambda c: c.update(estimatedTimeInMinutes=1 + 1 + 4 + 1)), "TM01")
    expect("CT01 contentType לא תקני", mutate(lambda c: c["subContent"][1].update(contentType="Practice")), "CT01")
    expect("TF01 true-false בעברית", mutate(lambda c: c["subContent"][1]["questions"][1].update(answers=["נכון", "לא נכון"], correctAnswers=["נכון"])), "TF01")
    expect("CH01 תשובה נכונה לא באפשרויות", mutate(lambda c: c["subContent"][1]["questions"][0].update(correctAnswers=["ג"])), "CH01")
    expect("SE01 תרגול מונחה עם שאלה", mutate(lambda c: (c["subContent"][1].update(contentType="solved-exercise"), c.update(estimatedTimeInMinutes=1 + 4 + 5))), "SE01")
    expect("TX01 U+200E בתשובה", mutate(lambda c: c["subContent"][1]["questions"][0].update(answers=["א‎.", "ב"], correctAnswers=["א‎."])), "TX01")
    expect("TX02 x נטוי מתמטי", mutate(lambda c: c["subContent"][1]["questions"][0].update(answers=["2\U0001D465", "ב"], correctAnswers=["ב"])), "TX02")
    expect("TX03 רווח בסוף תשובה", mutate(lambda c: c["subContent"][1]["questions"][0].update(answers=["א ", "ב"], correctAnswers=["ב"])), "TX03")
    expect("TX04 ש״ח מעורב", mutate(lambda c: c["subContent"][1]["questions"][0].update(answers=['32 ש״ח', '36 ש"ח'], correctAnswers=['32 ש״ח'])), "TX04")
    expect("TX05 יחס עם רווחים", mutate(lambda c: c["subContent"][1]["questions"][0].update(answers=["4 : 3", "ב"], correctAnswers=["ב"])), "TX05")
    expect("IB01 חסר סעיף בוט", mutate(lambda c: c["subContent"][0].update(informationToBot="מטרת הפריט: x.")), "IB01")
    expect("ID01 מזהה לא URL", mutate(lambda c: c.update(id="methodica-math-ratio-01-01")), "ID01")
    expect("ID02 מספור עם חור", mutate(lambda c: c["subContent"][2].update(id=BASE + "methodica-math-ratio-01-01-004/")), "ID02")
    expect("PF01 performance בלי response", mutate(lambda c: (c["subContent"][1]["questions"].append(q("performance", None, [{"stepId": "מונה"}])), c.update(estimatedTimeInMinutes=1 + 6 + 5))), "PF01")
    good_perf = mutate(lambda c: (c["subContent"][1]["questions"].append(q("performance", None, [{"stepId": "מונה", "response": "6"}, {"stepId": "מכנה", "response": "14"}])), c.update(estimatedTimeInMinutes=1 + 6 + 5)))
    good_perf["c.json"]["subContent"][1]["informationToBot"] = BOT + " אפשרויות בכל רשימה: א, ב."
    expect("performance תקין (stepId/response) עובר", good_perf, want_clean=True)
    legacy = mutate(lambda c: (c["subContent"][1]["questions"].append({**q("performance", None, None), "steps": [{"name": "מונה", "type": "text", "correctAnswer": "6"}]}), c.update(estimatedTimeInMinutes=1 + 6 + 5)))
    legacy["c.json"]["subContent"][1]["informationToBot"] = BOT + " אפשרויות בכל רשימה: א, ב."
    expect("PF01 סכימה ישנה (steps) מזוהה", legacy, "PF01")
    alt = mutate(lambda c: (c["subContent"][1]["questions"].append(q("matching", {"source": ["בושם", "קובייה"], "target": ["מל", "סמק"]}, [[{"source": "בושם", "target": "מל"}, {"source": "קובייה", "target": "סמק"}], [{"source": "בושם", "target": "סמק"}, {"source": "קובייה", "target": "מל"}]])), c.update(estimatedTimeInMinutes=1 + 6 + 5)))
    alt["c.json"]["subContent"][1]["informationToBot"] = BOT + " אפשרויות: מל, סמק."
    expect("תשובות חלופיות מקוננות (matching) עוברות", alt, want_clean=True)
    alt_bad = copy.deepcopy(alt)
    alt_bad["c.json"]["subContent"][1]["questions"][2]["correctAnswers"][1][0]["target"] = "לא-קיים"
    expect("MA01 זוג שגוי בתוך תשובה חלופית מקוננת", alt_bad, "MA01")
    alt_sp = copy.deepcopy(alt)
    alt_sp["c.json"]["subContent"][1]["questions"][2]["correctAnswers"][0][0]["target"] = "מל "
    alt_sp["c.json"]["subContent"][1]["questions"][2]["answers"]["target"] = ["מל ", "סמק"]
    expect("TX03 רווח בקצה בתוך תשובה מקוננת", alt_sp, "TX03")
    expect("RS01 מפריד שמור באפשרות", mutate(lambda c: c["subContent"][1]["questions"][0].update(answers=["א[,]ב", "ג"], correctAnswers=["ג"])), "RS01")
    expect("DD01 performance בלי אפשרויות ובלי אזכור", mutate(lambda c: (c["subContent"][1].update(informationToBot=BOT), c["subContent"][1]["questions"].append(q("performance", None, [{"stepId": "מונה", "response": "6"}])), c.update(estimatedTimeInMinutes=1 + 6 + 5))), "DD01")
    expect("MA01 matching מחוץ לרשימה", mutate(lambda c: (c["subContent"][1]["questions"].append(q("matching", {"source": ["א"], "target": ["1"]}, [{"source": "ב", "target": "1"}])), c.update(estimatedTimeInMinutes=1 + 6 + 5))), "MA01")

    # ערבית
    ar = good_component()
    ar["languages"] = ["Arabic"]
    ar["title"] = "الفهم"
    for it in ar["subContent"]:
        it["title"] = "تمرين 1" if "משימה מחוץ למחשב" not in it["title"] else "مهمّة ميدانية"
    for it in ar["subContent"]:
        for qq in it["questions"]:
            qq["questionText"] = "سؤال؟"
            if qq["questionType"] == "choice":
                qq["answers"], qq["correctAnswers"] = ["أ", "ب"], ["أ"]
    expect("ערבית תקינה עוברת", {"ar.json": ar}, want_clean=True)
    ar2 = copy.deepcopy(ar)
    ar2["subContent"][1]["questions"][0]["answers"] = ["نعم شחר", "ب"]
    ar2["subContent"][1]["questions"][0]["correctAnswers"] = ["ب"]
    expect("AR01 עברית בשדה ערבי", {"ar.json": ar2}, "AR01")
    ar3 = copy.deepcopy(ar)
    ar3["subContent"][1]["questions"][0]["questionText"] = "على على الكرة"
    expect("AR02 מילה כפולה", {"ar.json": ar3}, "AR02")
    ar4 = copy.deepcopy(ar)
    ar4["subContent"][1]["questions"][0]["questionText"] = "مساحة المثلثACD"
    expect("AR02 לטינית צמודה", {"ar.json": ar4}, "AR02")

    # זוגות
    he = good_component()
    he_files = {"methodica-math-ratio-01-01.json": he}
    ar_same = copy.deepcopy(ar)
    expect("זוג זהה עובר (למעט WARN של bot אם שונה)", {**he_files, "methodica-ar-math-ratio-01-01.json": ar_same}, want_clean=True)
    ar_bad = copy.deepcopy(ar)
    ar_bad["order"] = 2
    expect("PR01 order שונה", {**he_files, "methodica-ar-math-ratio-01-01.json": ar_bad}, "PR01")
    ar_bad2 = copy.deepcopy(ar)
    ar_bad2["subContent"] = ar_bad2["subContent"][:2]
    ar_bad2["estimatedTimeInMinutes"] = 1 + 4
    expect("PR02 מספר פריטים שונה", {**he_files, "methodica-ar-math-ratio-01-01.json": ar_bad2}, "PR02")
    ar_bad3 = copy.deepcopy(ar)
    ar_bad3["subContent"][1]["informationToBot"] = BOT + " עוד."
    expect("PR03 bot שונה", {**he_files, "methodica-ar-math-ratio-01-01.json": ar_bad3}, "PR03")

    # יחידה
    unit = {"id": "methodica-math-ratio-01", "title": "כותרת ארוכה מאוד מאוד מאוד שעוברת שלושים תווים"}
    expect("UN01 כותרת יחידה ארוכה", {"methodica-math-ratio-01_unit.json": unit}, "UN01")

    print()
    if FAILS:
        print(f"נכשלו {len(FAILS)} בדיקות: {FAILS}")
        return 1
    print("כל הבדיקות עברו.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
