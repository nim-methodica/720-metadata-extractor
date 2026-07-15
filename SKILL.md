---
name: 720-metadata-extractor
description: >-
  Extracts metadata JSON files from 720/methodica training script PPTX files per the
  720 Content Metadata standard (V2.1+). Given a script PPTX, produces one unit-level
  JSON plus one JSON per רכיב (component) with all פריטים (items) nested inside
  `subContent[]`. Use whenever the user asks to extract/generate/produce metadata,
  מטה־דאטה, or JSON from a 720 script — filenames typically contain "יעד" and IDs
  follow `methodica-<subject>-<topic>-XX`. Handles subject-agnostic content (math,
  science, and beyond). **Fully autonomous** — does not ask the user for
  prerequisiteLearningObjective, recommendedAfterFail, componentPurpose, isAssessment,
  cognitiveLevel, depthLevel, relativeDifficulty, estimatedTime, or contentType. All
  these are determined by deterministic rules in references/conventions.md.
  Only stops and asks the user if: the script lacks item-level IDs ("מספר פריט" tags),
  or the unit ID is not in learning-objectives.json even after refreshing from the
  management Excel (meaning a brand new objective). Empty subTopic / learningObjective
  in slide 1 falls back to values from learning-objectives.json, not a stop.
  Do NOT use for QA of scripts (720-script-qa), building scripts from Word
  (720-script-writer), or generic PPTX metadata extraction unrelated to 720.
---

# 720-metadata-extractor

מפיק קבצי מטא־דאטה JSON מתסריט 720 (PPTX), לפי תקן "תיאור טכני של מאפייני תוכן לפלטפורמות
720" (V2.1). כללי לכל 720 — לא תלוי במקצוע ולא בפרויקט ספציפי.

**עקרון-על: הסקיל אוטונומי לחלוטין.** כל השדות שאפשר לגזור מהתסריט או מהמוסכמות — נגזרים
אוטומטית. הסקיל *לא* שואל את המשתמש שאלות שיש להן תשובה דטרמיניסטית. הכללים המלאים
ב-`references/conventions.md` — לקרוא לפני התחלת עבודה.

## קבצי רקע (לקרוא לפני התחלת עבודה)

- `references/standard.md` — התקן המלא: השדות ברמות יחידה/רכיב/פריט, כל הרשימות הסגורות.
- `references/conventions.md` — **הכללים הדטרמיניסטיים.** מכיל את כל התשובות שהמשתמש נתן
  בעבר, כדי שהסקיל לא ישאל אותן שוב.
- `references/question-types.md` — איך לזהות סוג שאלה והמבנה של `answers`/`correctAnswers`.
- `references/cognitive-levels-detailed.md` — הגדרות מפורטות של רמות החשיבה של הראמ"ה
  (4 רמות למתמטיקה, 3 רמות למדעים) — לצורך בחירה מדויקת של `cognitiveLevel`.
- `references/example-output.md` — דוגמאות JSON ממשיות.
- `references/learning-objectives.json` — רשימת סדר יעדי הלמידה (מתמטיקה + מדעים), לחישוב
  `prerequisiteLearningObjective`. מתעדכן מקובץ ניהול 720 באמצעות `scripts/refresh_objectives.py`.
  **מכיל גם מיפוי לקודי MOE** (`moe_code` + `subtopic_code`) שמשמשים ל-`learningObjective`
  ו-`subTopic` בפלט. מיפוי חלקי — לא כל היעדים נמצאים באינדקסי משרד החינוך עדיין.
- `references/moe-index.json` — האינדקס הרשמי של משרד החינוך (מקצוע → תחום → נושא → תת-נושא
  → יעד למידה + קוד). מתרענן מקובצי אקסל של משרד החינוך באמצעות `scripts/refresh_moe_index.py`.
- `scripts/url_builder.py` — ממיר ID קצר ל-URL מלא לפי החוק שמופיע ב-`conventions.md`.
  הפלט של הסקיל **חייב** לכלול URLים מלאים (לא IDים קצרים) בכל שדה שמכיל id.
- `scripts/lookup_moe.py` — מקבל methodica ID ומחזיר את `moe_code`, `subtopic_code`
  והמידע העברי המתלווה. משמש למילוי `learningObjective` ו-`subTopic` במטא-דאטה.

## מבנה הפלט

**הפלט הוא לא קובץ אחד**. הפלטפורמה מעלה כל רכיב בנפרד, ולכן:

- **קובץ יחידה יחיד** (`<unit-id>_unit.json`) — שדות היחידה בלבד, בלי הרכיבים.
- **קובץ נפרד לכל רכיב** (`<component-id>.json`) — שדות הרכיב + `learningUnitId` (הפניה
  ל-ID של היחידה) + `subContent[]` עם כל הפריטים מקוננים.

הפריטים תמיד תחת `subContent[]` של הרכיב שלהם. **לעולם לא** קבצים נפרדים.

## התהליך

### שלב 1 — חילוץ וזיהוי מבנה

הרץ:

```bash
python scripts/extract_slides.py "<path/to/script.pptx>" <output-dir>
```

הסקריפט מפיק:
- `slides.txt` — טקסט מלא של כל שקף
- `mapping.txt` — טבלת שקף → item-id → תקציר תוכן

ומדפיס סיכום: מספר שקפים, מספר פריטים, מספר רכיבים, ה-ID של כל רכיב + מספר הפריטים בו.

**עצור ובקש מהמשתמש** רק אם:
- אין תוויות `מספר פריט` בשקפים (הסקריפט מדפיס אזהרה).
- מבנה חריג — פחות מ-5 או יותר מ-6 רכיבים (ראה `conventions.md`).

### שלב 2 — חילוץ שדות היחידה

קרא את `slides.txt` — שקף 1 מכיל את:
- שם הנושא → `subTopic`
- פירוט היעד → `learningObjective`
- ID → ה-`id` של היחידה (`methodica-<subject>-<topic>-XX`)

לחישוב `prerequisiteLearningObjective`:

```bash
python scripts/lookup_prerequisite.py <unit-id>
```

מחזיר את ה-ID של היעד הקודם, או שורה ריקה אם זה היעד הראשון.

**Fallback רך** (הסקיל אוטונומי — לא עוצר, אלא ממלא ומדווח):

- אם `subTopic` **ריק** בשקף 1 — קח את שם הנושא מ-`learning-objectives.json` (השדה `topic`
  של הרשומה המתאימה ל-ID). דווח למשתמש שהשדה היה ריק בשקף 1.
- אם `learningObjective` **ריק** בשקף 1 — קח את השדה `objective` מ-`learning-objectives.json`.
  דווח למשתמש.
- אם ה-ID **לא נמצא** ב-`learning-objectives.json` — הרץ `refresh_objectives.py` על קובץ
  הניהול. אם עדיין לא נמצא — כאן **כן עצור** ובקש מהמשתמש את פרטי היעד החדש (זהו יעד
  חדש שטרם נכנס לקובץ הניהול).

כל שאר שדות היחידה (`targetSector`, `targetAudience`) — ברירות מחדל קבועות מ-`conventions.md`.

### שלב 3 — בניית קובץ היחידה

צור `<unit-id>_unit.json` בתיקיית הפלט. ראה תבנית ב-`references/example-output.md`.

### שלב 4 — לכל רכיב: קבע שדות ופריטים

לכל רכיב שזוהה בשלב 1:

1. **קבע `componentPurpose`, `isAssessment`, `depthLevel`, `cognitiveLevel`, `relativeDifficulty`
   ו-`recommendedAfterFail`** — לפי טבלאות ב-`conventions.md` (כל שדה יש לו כלל דטרמיניסטי).

2. **לכל פריט ברכיב:**
   - קרא את השקפים של הפריט מ-`slides.txt` (לפי טווח שהוצג ב-`mapping.txt`).
   - קבע `title` לפי תבנית `<סוג התרגיל> <מספר>: <תיאור>` (`conventions.md` #12).
   - קבע `contentType` לפי סוג הפריט (`conventions.md` #6).
   - `mediaFormat: "Interactive content"` כברירת מחדל.
   - חלץ שאלות לתוך `questions[]` — זיהוי `questionType` וכתיבת `answers`/`correctAnswers`
     לפי `references/question-types.md`.
   - כתוב `informationToBot` במבנה 4 החלקים: מטרה / כיווני חשיבה / טעויות נפוצות / מידע נוסף.

3. **חישוב `estimatedTimeInMinutes`** — סכום סעיפים ברכיב × 2 דקות. פריט בלי שאלה = 1 דקה.

### שלב 5 — כתיבת קבצי הרכיבים

צור `<component-id>.json` לכל רכיב, עם `subContent[]` שמכיל את כל הפריטים.

### שלב 6 — מסירה למשתמש

הצג:
1. רשימת הקבצים שנוצרו.
2. סיכום קצר: מספר רכיבים, מספר פריטים, סכום `estimatedTimeInMinutes` של היחידה.
3. **רק** אזהרות/בעיות שלא נפתרו:
   - שאלת matching שלא הצלחת לזהות מהטקסט את מבנה `source/target` (למשל תמונות בשאלה).
   - פריט עם `correctAnswers` ריק (משימת כיתה או פריט העשרה).
   - כל חריגה מהמוסכמות בקובץ ההגדרות.

## מה הסקיל **לא** שואל את המשתמש (בעבר שאל, עכשיו לא)

- ❌ `prerequisiteLearningObjective` — נגזר מ-`learning-objectives.json`
- ❌ `subTopic` / `learningObjective` — משקף 1
- ❌ מבנה של רכיבים — 5 או 6 לפי הקובץ
- ❌ `recommendedAfterFail` — חוק פשוט (רק רכיב 1 → רכיב 2)
- ❌ `isAssessment` — רק רכיבים 5-6
- ❌ `componentPurpose` — לפי הרכיב
- ❌ `contentType` — 3 קטגוריות לפי סוג הפריט
- ❌ `mediaFormat` — Interactive content כברירת מחדל
- ❌ `cognitiveLevel` — לפי מקצוע + רכיב
- ❌ `depthLevel` — Basic חוץ ממתקדם
- ❌ `relativeDifficulty` — לפי סוג התרגילים
- ❌ `estimatedTimeInMinutes` — 2 דקות לסעיף

## דגשים לביצוע

- **RTL / עברית**: הטקסט בשקפים מפוצל ב-XML לפעמים לרסיסים. הסקריפט מאחד — הסתמך על טקסט
  מחובר, לא על מראה חזותי.
- **תאריך `createdAt`/`updatedAt`** — היום. הריצו `date -u +"%Y-%m-%dT%H:%M:%S.000Z"` ב-Bash
  אם צריך זמן מדויק.
- **תיקיית פלט** — צור `output-<unit-id>/` לצד קובץ ה-PPTX, לא בתיקייה זמנית.
- **קבצים גדולים** — תסריטי 720 יכולים להיות 100+ MB (עם תמונות/וידאו מוטמעים). הסקריפט
  לא מתעסק במדיה, רק ב-XML של השקפים.
