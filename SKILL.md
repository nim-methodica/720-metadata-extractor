---
name: 720-metadata-extractor
description: >-
  Extracts metadata JSON files from 720/methodica training script PPTX files per the
  720 Content Metadata standard (V2.1+). Given a script PPTX, produces one unit-level
  JSON plus one JSON per רכיב (component) with all פריטים (items) nested inside
  `subContent[]`. Use whenever the user asks to extract/generate/produce metadata,
  מטה־דאטה, or JSON from a 720 script — filenames typically contain "יעד" and IDs
  follow `methodica-<subject>-<topic>-XX`. Handles subject-agnostic content (math,
  science, and beyond) and follows the fixed defaults + per-component conventions
  captured in references/conventions.md.
  Stops and asks the user (does not guess blind) whenever: the script lacks item-level
  IDs ("מספר פריט" tags), the number of רכיבים deviates from the 4-or-5 pattern, or
  fields not derivable from the script are needed (prerequisiteLearningObjective,
  recommendedAfterFail beyond convention). Do NOT use for QA of scripts (720-script-qa),
  building scripts from Word (720-script-writer), or generic PPTX metadata extraction
  unrelated to 720.
---

# 720-metadata-extractor

מפיק קבצי מטא־דאטה JSON מתסריט 720 (PPTX), לפי תקן "תיאור טכני של מאפייני תוכן לפלטפורמות 720"
(V2.1). כללי לכל 720 — לא תלוי במקצוע ולא בפרויקט ספציפי.

**עקרון-על: הסקיל קורא את התסריט ומחלץ את מה שכתוב שם. שדות שלא ניתן להסיק מהתסריט (יעדי
קדימות, אינדקסים של מיומנויות, ועוד) — שואלים את המשתמש. הערכות של רמת קושי/רמת חשיבה/סוג
תוכן — הסקיל מבצע לפי הכללים ב-`references/conventions.md`, לא ניחוש חופשי.**

## קבצי רקע (לקרוא לפני התחלת עבודה)

- `references/standard.md` — התקן המלא: השדות ברמות יחידה/רכיב/פריט, כל הרשימות הסגורות.
- `references/conventions.md` — המוסכמות שסוכמו בפועל: ברירות מחדל קבועות, כללים לפי רכיב,
  איך מחשבים estimatedTime, מיפוי componentPurpose, מתי מסמנים isAssessment.
- `references/question-types.md` — איך לזהות סוג שאלה (choice/true-false/fill-in/numeric/
  matching/sequencing) לפי מראה השקף, ואיך למלא `answers`/`correctAnswers` לכל סוג.

## מבנה הפלט

לפני שמתחילים לכתוב JSON, חשוב להבין: **הפלט הוא לא קובץ אחד**. הפלטפורמה מעלה כל רכיב
בנפרד, ולכן:

- **קובץ יחידה יחיד** (`<unit-id>_unit.json`) — מכיל *רק* את שדות היחידה, בלי הרכיבים.
- **קובץ נפרד לכל רכיב** (`<component-id>.json`) — מכיל את שדות הרכיב + `learningUnitId`
  (הפניה בלבד ל-ID של היחידה, לא כל המטא־דאטה שלה) + `subContent[]` עם כל הפריטים מקוננים.

הפריטים **לעולם לא** קבצים נפרדים — הם תמיד תחת `subContent[]` של הרכיב שלהם.

## תהליך העבודה

### שלב 1 — חילוץ תוכן וזיהוי מבנה

הרץ את הסקריפט לחילוץ שקפים ומיפוי לפריטים:

```bash
python scripts/extract_slides.py "<path/to/script.pptx>" <output-dir>
```

הסקריפט:
1. מפרק את ה-PPTX (unzip) ומחלץ טקסט מכל שקף.
2. מזהה את שקף 1 ("פרטים על היעד") ומחלץ ממנו: ID היחידה, שם נושא, פירוט יעד, מבנה
   (כמויות שאלות, מסך בחירת דמות, פלייליסט, נטפליקס, פריט העשרה, כותבי תוכן, תאריך).
3. מזהה שקפי מפריד רכיב (`רכיב:` / `רכיב ראשון` וכו') עם ID מלא של רכיב.
4. מזהה תוויות `מספר פריט` בכל שקף עם ID מלא של פריט.
5. מפיק שני קבצי עזר ב-`<output-dir>`:
   - `slides.txt` — טקסט מלא של כל שקף
   - `mapping.txt` — טבלת שקף → item-id → תקציר תוכן

### שלב 2 — ולידציה של המיפוי

בדוק שיש `מספר פריט` בכל שקף רלוונטי. אם חסר — **עצור ובקש מהמשתמש להוסיף מספרי פריט
בקובץ**. אין להמציא מיפוי לפי ניחוש (זה יגרום לפירוק שגוי של תוכן לפריטים).

הצג למשתמש טבלה של רכיבים ופריטים שזוהו, למשל:

| רכיב | תיאור | מספר פריטים | טווח שקפים |
|---|---|---|---|
| 01-01 | פתיחה + הקנייה + סטנדרטי | 10 | 5-72 |
| 01-02 | תרגול בסיסי + סטנדרטי ב | 3 | 73-94 |
| ...

### שלב 3 — שאלות פתוחות למשתמש

לפני שכותבים JSON, ודא ששאלת את המשתמש על השדות שאי אפשר לגזור מהתסריט (ראה
`references/conventions.md` לרשימה מלאה):

1. **prerequisiteLearningObjective** — יעדי קדימות (ID של יעדים שהלומד אמור לדעת קודם).
2. **recommendedAfterFail חריגות** — כברירת מחדל: רכיב 2 → רכיב 1, רכיב 4 → רכיב 2, שאר
   ריקים. אם הכתיבה בקובץ מסמנת אחרת (למשל אינטרו לרכיב שקורא לחזור למקום אחר) — שאל.
2a. **subTopic ו-learningObjective** — אם לא מופיעים ישירות בשקף 1, בקש הבהרה.
3. **מבנה חריג** — אם מספר הרכיבים אינו 4 או 5, או שיש רכיב שלא מתאים לתבנית
   (הקנייה/תרגול/משימה/הערכה) — אשר עם המשתמש.
4. **פריט העשרה / שאלת שיא** — ודא איזה רכיב מכיל אותם ואם הם משפיעים על
   `isAssessment` של הרכיב.

### שלב 4 — כתיבת ה-JSON

לכל רכיב, בנה קובץ JSON לפי המבנה ב-`references/standard.md`:

- **שדות של רכיב**: id, title, learningUnitId, componentPurpose, isAssessment, manufacture,
  recommendedAfterFail, isRequired, relativeDifficulty, order, depthLevel, cognitiveLevel,
  languages, skills, estimatedTimeInMinutes, createdAt, updatedAt, subContent.
- **שדות של פריט** (בתוך `subContent[]`): id, title, informationToBot, contentType,
  mediaFormat, questions[].

עקרונות מפתח לכתיבה:

- `informationToBot` — ארבעה חלקים במחרוזת אחת: **מטרת הפריט**, **מה התלמיד אמור להבין/
  לתרגל + כיווני חשיבה ואסטרטגיות**, **טעויות נפוצות**, **מידע נוסף + צילום מסך**.
  זה מה שהבוט יראה — פרט מספיק בלי לכתוב רומן.
- `questionType` — לפי `references/question-types.md`. תשובה מספרית טהורה → `numeric`.
  יחס עם ":1" → `fill-in` עם ואריאנטים לפסיק/רווח. matching עם `source/target`.
- `answers`/`correctAnswers` — הפורמט משתנה לפי `questionType`, ראה טבלה בקובץ הנ"ל.
- **פורמט תאריכים ISO 8601**: `2026-06-24T00:00:00.000Z`. השתמש בתאריך של היום כברירת
  מחדל (אלא אם המשתמש מבקש אחרת).

### שלב 5 — מסירה

הצג למשתמש:
1. רשימת הקבצים שנוצרו (יחידה + N רכיבים).
2. סיכום קצר של השדות שנקבעו בשיקול דעת (`estimatedTimeInMinutes`, `relativeDifficulty`,
   `cognitiveLevel`, `depthLevel`, `contentType` של פריטים) — כדי שהמשתמש יבדוק.
3. שאלות/אזהרות לא נפתרו (למשל שאלת matching שלא הצלחת לזהות מהטקסט מה בכל תמונה).

## דגשים לביצוע

- **RTL / עברית**: הטקסט בשקפים מפוצל ב-XML לעיתים לרסיסים (מילה כל מסגרת). הסקריפט
  מאחד — לא מסתמכים על המראה הוויזואלי, על הטקסט המחובר.
- **תאריך createdAt/updatedAt** — היום, בפורמט ISO. אין לך גישה ל-`Date.now()` בסביבות
  מסוימות; אפשר להשתמש ב-Bash `date -u +"%Y-%m-%dT%H:%M:%S.000Z"` אם צריך זמן מדויק.
- **תיקיית פלט** — צור `output/` (או `output-<subject>/`) לצד קובץ ה-PPTX, לא בתיקייה
  זמנית. המשתמש יעביר את הקבצים למתכנת.
- **קבצים גדולים** — תסריטי 720 יכולים להיות 100+ MB (עם תמונות/וידאו מוטמעים). הסקריפט
  לא מתעסק במדיה, רק ב-XML של השקפים.
