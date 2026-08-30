---
name: 720-metadata-extractor
description: >-
  Extracts metadata JSON from 720/methodica content per the 720 Content Metadata
  standard (V2.1+): one unit-level JSON + one per רכיב (component), פריטים (items)
  nested in `subContent[]`. Handles THREE source types: (1) a training script PPTX
  (filenames typically contain "יעד", IDs follow `methodica-{subject}-{topic}-XX`);
  (2) a live Articulate Storyline HTML5 STEM unit (a `story.html` URL, no local file);
  (3) an already-produced/built 720 learning unit — a local HTML/CSS/JS SPA
  (`index.html`+`script.js`, often `registry.js`) that IS the final deliverable, not a
  script for one. Use when asked to extract/generate/produce metadata, מטה־דאטה, or
  JSON from any of these. **Fully autonomous** — never asks about deterministic fields
  (cognitiveLevels, depthLevel, masteryLevel, etc.); all
  determined by rules in references/conventions.md. Only stops to ask if: the source
  lacks item-level boundaries in an unresolvable way, the unit ID isn't in
  learning-objectives.json even after refreshing (brand-new objective), or a question's
  correct answer (esp. matching) depends on image content with no text description. Do
  NOT use for: QA of scripts (720-script-qa), building scripts from Word
  (720-script-writer), or generic PPTX/HTML metadata extraction unrelated to 720.
---

# 720-metadata-extractor

מפיק קבצי מטא־דאטה JSON מתסריט 720 (PPTX), לפי תקן "תיאור טכני של מאפייני תוכן לפלטפורמות
720" (V2.5). כללי לכל 720 — לא תלוי במקצוע ולא בפרויקט ספציפי.

**עקרון-על: הסקיל אוטונומי לחלוטין.** כל השדות שאפשר לגזור מהתסריט או מהמוסכמות — נגזרים
אוטומטית. הסקיל *לא* שואל את המשתמש שאלות שיש להן תשובה דטרמיניסטית. הכללים המלאים
ב-`references/conventions.md` — לקרוא לפני התחלת עבודה.

**יוצא דופן יחיד**: כשתשובה נכונה (בעיקר `correctAnswers` של `matching`) תלויה בתוכן שמופיע
רק כתמונה/גרפיקה בשקף, בלי תיאור טקסטואלי — הסקיל **עוצר ושואל** את המשתמש, כדי שהפלט
הסופי יהיה מלא ולא יכיל ניחושים או שדות ריקים. ראה `references/conventions.md`.

## קבצי רקע (לקרוא לפני התחלת עבודה)

- `references/standard.md` — התקן המלא: השדות ברמות יחידה/רכיב/פריט, כל הרשימות הסגורות.
- `references/conventions.md` — **הכללים הדטרמיניסטיים.** מכיל את כל התשובות שהמשתמש נתן
  בעבר, כדי שהסקיל לא ישאל אותן שוב.
- `references/question-types.md` — איך לזהות סוג שאלה והמבנה של `answers`/`correctAnswers`.
- `references/cognitive-levels-detailed.md` — הגדרות מפורטות של רמות החשיבה של הראמ"ה
  (4 רמות למתמטיקה, 3 רמות למדעים) — לצורך בחירה מדויקת של `cognitiveLevels`.
- `references/example-output.md` — דוגמאות JSON ממשיות.
- `references/learning-objectives.json` — רשימת סדר יעדי הלמידה (מתמטיקה + מדעים), **מכיל
  מיפוי לקודי MOE** (`moe_code` + `subtopic_code`) שמשמשים ל-`learningObjective` ו-`subTopic`
  בפלט. מתעדכן מקובץ ניהול 720 באמצעות `scripts/refresh_objectives.py`. מיפוי חלקי — לא כל
  היעדים נמצאים באינדקסי משרד החינוך עדיין.
- `references/moe-index.json` — האינדקס הרשמי של משרד החינוך (מקצוע → תחום → נושא → תת-נושא
  → יעד למידה + קוד). מתרענן מקובצי אקסל של משרד החינוך באמצעות `scripts/refresh_moe_index.py`.
- `scripts/url_builder.py` — ממיר ID קצר ל-URL מלא עבור רכיב/פריט, לפי החוק שמופיע ב-
  `conventions.md`. **עבור ID ברמת יחידה מחזיר את ה-ID הקצר כפי שהוא** (V2.5 — אין חובת
  IRI ביחידה). הפלט של הסקיל **חייב** לכלול URLים מלאים ברמת רכיב/פריט (לא IDים קצרים).
- `scripts/lookup_moe.py` — מקבל methodica ID ומחזיר את `moe_code`, `subtopic_code`
  והמידע העברי המתלווה. משמש למילוי `learningObjective` ו-`subTopic` במטא-דאטה.
- `scripts/extract_storyline_slides.py` — כמו `extract_slides.py`, אבל למקור מס' 2:
  לומדת STEM חיה בפורמט Articulate Storyline (HTML5, `story.html` ברשת, אין קובץ מקומי).
  ראו `conventions.md`, "מקרה ייחודי: לומדות STEM".
- `scripts/extract_produced_unit_slides.py` — כמו `extract_slides.py`, אבל למקור מס' 3:
  יחידת 720 **מופקת** — SPA בנוי מקומית ב-HTML/CSS/JS שכבר *הוא* התוצר הסופי (לא תסריט
  שממנו בונים לומדה). ראו `conventions.md`, "מקרה ייחודי: יחידות 720 מופקות".

## מבנה הפלט

**הפלט הוא לא קובץ אחד**. הפלטפורמה מעלה כל רכיב בנפרד, ולכן:

- **קובץ יחידה יחיד** (`{unit-id}_unit.json`) — שדות היחידה בלבד, בלי הרכיבים.
- **קובץ נפרד לכל רכיב** (`{component-id}.json`) — שדות הרכיב + `learningUnitId` (הפניה
  ל-ID של היחידה) + `subContent[]` עם כל הפריטים מקוננים.

הפריטים תמיד תחת `subContent[]` של הרכיב שלהם. **לעולם לא** קבצים נפרדים.

## התהליך

### שלב 1 — זיהוי סוג המקור, חילוץ וזיהוי מבנה

**זהה קודם איזה משלושת סוגי המקור מדובר**:

| סוג מקור | סימנים מזהים | סקריפט |
|---|---|---|
| 1. תסריט PPTX | קובץ `.pptx`, בד"כ עם "יעד" בשם הקובץ | `scripts/extract_slides.py` |
| 2. Storyline חי | URL שמסתיים ב-`story.html`, אין קובץ מקומי | `scripts/extract_storyline_slides.py` |
| 3. יחידה מופקת | תיקייה מקומית עם `index.html`+`script.js` (לרוב גם `registry.js`) — היחידה עצמה, לא תסריט | `scripts/extract_produced_unit_slides.py` |

הרץ את הסקריפט המתאים, למשל למקור 1:

```bash
python scripts/extract_slides.py "{path/to/script.pptx}" {output-dir}
```

או למקור 3:

```bash
python scripts/extract_produced_unit_slides.py "{path/to/project-dir}" {output-dir}
```

כל סקריפט מפיק:
- `slides.txt` — טקסט מלא של כל שקף/מסך
- `mapping.txt` — טבלת שקף/מסך → item-id → תקציר תוכן

ומדפיס סיכום: מספר שקפים/מסכים, מספר פריטים (למקור 1), מספר רכיבים, ה-ID של כל רכיב +
מספר הפריטים בו. **למקורות 2 ו-3 אין תיוג "מספר פריט" בקוד** — גבולות הפריט נקבעים לפי
הכללים הייעודיים ב-`conventions.md` (חיפוש "STEM"/"מופקות" בהתאמה), לא ע"י הסקריפט.

**עצור ובקש מהמשתמש** רק אם:
- מקור 1: אין תוויות `מספר פריט` בשקפים (הסקריפט מדפיס אזהרה).
- מקור 1: מבנה חריג — פחות מ-5 או יותר מ-6 רכיבים (ראה `conventions.md`).
- מקור 3: אין `docs/03-content-map.md` (או שווה-ערך) **וגם** התסריט המקורי (Word) לא זמין —
  אין דרך לשחזר את המספור המקורי של השאלות/סעיפים, ולכן אי אפשר לקבוע גבולות פריט באמינות.

### שלב 2 — חילוץ שדות היחידה

**מקור 1 (PPTX)**: קרא את `slides.txt` — שקף 1 מכיל את:
- שם הנושא → `subTopic`
- פירוט היעד → `learningObjective`
- ID → ה-`id` של היחידה (`methodica-{subject}-{topic}-XX`)

**מקורות 2-3 (Storyline / יחידה מופקת)**: אין "שקף 1" תקני עם השדות האלו. ה-ID/נושא/יעד
לרוב לא נמצאים ב-`learning-objectives.json` (יחידת STEM/מיפוי חדשה) — קח אותם ישירות
מהמשתמש או מתיעוד הפרויקט (`docs/00-README.md` וכו'), ראה `conventions.md`.

**Fallback רך** (הסקיל אוטונומי — לא עוצר, אלא ממלא ומדווח):

- אם `subTopic` **ריק** בשקף 1 — קח את שם הנושא מ-`learning-objectives.json` (השדה `topic`
  של הרשומה המתאימה ל-ID). דווח למשתמש שהשדה היה ריק בשקף 1.
- אם `learningObjective` **ריק** בשקף 1 — קח את השדה `objective` מ-`learning-objectives.json`.
  דווח למשתמש.
- אם ה-ID **לא נמצא** ב-`learning-objectives.json` — הרץ `refresh_objectives.py` על קובץ
  הניהול. אם עדיין לא נמצא — כאן **כן עצור** ובקש מהמשתמש את פרטי היעד החדש (זהו יעד
  חדש שטרם נכנס לקובץ הניהול).

כל שאר שדות היחידה (`targetSectors`, `targetAudience`, `manufacturer`) — ברירות מחדל קבועות
מ-`conventions.md`.

### שלב 3 — בניית קובץ היחידה

צור `{unit-id}_unit.json` בתיקיית הפלט. ראה תבנית ב-`references/example-output.md`.

### שלב 4 — לכל רכיב: קבע שדות ופריטים

לכל רכיב שזוהה בשלב 1:

1. **קבע `componentPurpose`, `isAssessment`, `depthLevel`, `cognitiveLevels`, `relativeDifficulty`,
   `masteryLevel` ו-`recommendedAfterFail`** — לפי טבלאות ב-`conventions.md` (כל שדה יש לו כלל
   דטרמיניסטי). שים לב: `masteryLevel` של שאלת שיא (`intermediate`) שונה מ-`relativeDifficulty`
   שלה (5) — הם לא נגזרים זה מזה.

2. **לכל פריט ברכיב:**
   - קרא את השקפים של הפריט מ-`slides.txt` (לפי טווח שהוצג ב-`mapping.txt`).
   - קבע `title` לפי תבנית `{סוג התרגיל} {מספר}: {תיאור}` (`conventions.md` #12).
   - קבע `contentType` לפי סוג הפריט (`conventions.md` #6).
   - `mediaFormat: "content-interactive"` כברירת מחדל.
   - חלץ שאלות לתוך `questions[]` — זיהוי `questionType` וכתיבת `answers`/`correctAnswers`
     לפי `references/question-types.md`. **אם `correctAnswers` של `matching` (או כל שדה אחר)
     תלוי בתוכן שמופיע רק כתמונה/גרפיקה בלי תיאור טקסטואלי — עצור כאן ושאל את המשתמש** (ראה
     `question-types.md` ו-`conventions.md`). אל תנחש ואל תשאיר ריק.
   - כתוב `informationToBot` במבנה 4 החלקים: מטרה / כיווני חשיבה / טעויות נפוצות / מידע נוסף.

3. **חישוב `estimatedTimeInMinutes`** — סכום סעיפים ברכיב × 2 דקות. פריט בלי שאלה = 1 דקה.

### שלב 5 — כתיבת קבצי הרכיבים

צור `{component-id}.json` לכל רכיב, עם `subContent[]` שמכיל את כל הפריטים.

### שלב 6 — מסירה למשתמש

הצג:
1. רשימת הקבצים שנוצרו.
2. סיכום קצר: מספר רכיבים, מספר פריטים, סכום `estimatedTimeInMinutes` של היחידה.
3. **רק** אזהרות/בעיות שלא נפתרו (אמורות להיות נדירות — תוכן תלוי-תמונה כבר טופל בשלב 4
   באמצעות שאלה למשתמש, לא כאזהרה בדיעבד):
   - כל חריגה מהמוסכמות בקובץ ההגדרות.
   - שאלה שהמשתמש בחר לדלג עליה בשלב 4 ולא סיפק תשובה — ציין איזה פריט/שדה עדיין חסר.

## מה הסקיל **לא** שואל את המשתמש (בעבר שאל, עכשיו לא)

- ❌ `subTopic` / `learningObjective` — משקף 1
- ❌ מבנה של רכיבים — 5 או 6 לפי הקובץ
- ❌ `recommendedAfterFail` — חוק פשוט (רק רכיב הבסיסי → חזרה לרכיב 1)
- ❌ `isAssessment` — רק הרכיב שמכיל שאלת שיא (לא בהכרח רכיב 5/6)
- ❌ `isRequired` — `false` רק לרכיב הבסיסי, `true` לכל השאר
- ❌ `componentPurpose` — לפי הרכיב
- ❌ `contentType` — 3 קטגוריות לפי סוג הפריט
- ❌ `mediaFormat` — content-interactive כברירת מחדל
- ❌ `cognitiveLevels` — לפי מקצוע + רכיב
- ❌ `depthLevel` — Basic חוץ ממתקדם
- ❌ `relativeDifficulty` — לפי סוג התרגילים
- ❌ `masteryLevel` — לפי תפקיד הרכיב (שאלת שיא = intermediate, לא advanced)
- ❌ `estimatedTimeInMinutes` — 2 דקות לסעיף

## דגשים לביצוע

- **RTL / עברית**: הטקסט בשקפים מפוצל ב-XML לפעמים לרסיסים. הסקריפט מאחד — הסתמך על טקסט
  מחובר, לא על מראה חזותי.
- **תאריך `createdAt`/`updatedAt`** — היום. הריצו `date -u +"%Y-%m-%dT%H:%M:%S.000Z"` ב-Bash
  אם צריך זמן מדויק.
- **תיקיית פלט** — **לעולם אל תכתוב פלט (JSON/`slides.txt`/`mapping.txt`) לצד קובץ ה-PPTX
  אם הוא יושב בכונן ארגוני/משותף (FTP, Organization Data וכיו"ב)** — זו לא תיקיית עבודה
  אישית, ואסור להשאיר שם קבצים נגזרים בלי בקשה מפורשת. כתוב תמיד לתיקיית העבודה המקומית
  של הסקיל: `<תיקיית עבודה>\output\<מקצוע>\<מזהה יעד>\` (למשל
  `...\יצירת מטה דטה\output\מתמטיקה\יעד 2.1\`). רק אם קובץ המקור כבר יושב בתיקיית עבודה
  מקומית של המשתמש (לא כונן משותף) — מותר ליצור `output-{unit-id}/` לצידו.
- **קבצים גדולים** — תסריטי 720 יכולים להיות 100+ MB (עם תמונות/וידאו מוטמעים). הסקריפט
  לא מתעסק במדיה, רק ב-XML של השקפים.
