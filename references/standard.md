# תקן 720 Content Metadata (V2.3)

מסמך זה מסכם את התקן הטכני לתיאור מטא־דאטה של יחידות תוכן, רכיבים ופריטים לפלטפורמת 720.
המקור המלא: `הנחיות טכניות לפיתוח תוכן 720 - תשפז.pdf`.

**V2.3**: בכל טבלאות הרשימות הסגורות, ערכים בני יותר ממילה אחת נכתבים עם מקף (`-`) במקום
רווח, ובאותיות קטנות (למשל `Solved Exercise` → `exercise-solved`).

## מבנה היררכי

```
יחידת תוכן (Content Unit)
└── רכיבי תוכן (Components) — מערך components[]
    └── פריטי תוכן (Items) — מערך subContent[]
        └── שאלות (Questions) — מערך questions[]
```

בפלט מטא־דאטה: **קובץ יחידה** נפרד, ו**קובץ נפרד לכל רכיב** (מכיל את הפריטים שלו כ-
`subContent[]`, ואת ה-`learningUnitId` כהפניה בלבד ליחידה). פריטים אינם קבצים נפרדים.

## שדות יחידת תוכן

| שדה | סוג | תיאור |
|---|---|---|
| `id` | string | מזהה חד-חד־ערכי לכל יחידה. תבנית: `methodica-<subject>-<topic>-XX`. |
| `title` | string ≤30 תווים | כותרת תצוגתית של היחידה. |
| `subTopic` | string | מזהה מרשימת תתי־נושאים סגורה (בעבודה). בפועל: שם הנושא בעברית. |
| `learningObjective` | string | מזהה מרשימת יעדי למידה סגורה (בעבודה). בפועל: פירוט היעד. |
| `targetSector` | array | רשימת מגזרים (state-general / religious-state / orthodox / arab-sector / druze-sector / bedouin-sector / education-special). |
| `targetAudience` | array | רשימת אוכלוסיות (general / excellent / populations-disadvantaged / immigrants-new / needs-special-with-students / gaps-language-with-students / at-risk-students). |
| `prerequisiteLearningObjective` | array | מערך של אינדקסים של יעדי למידה נדרשים לפני היחידה (לפי הגדרת יצירת התוכן, לא ע"י המשרד). |

## שדות רכיב תוכן

| שדה | סוג | תיאור |
|---|---|---|
| `id` | string | מזהה חד-חד־ערכי לכל רכיב. תבנית: `<unit-id>-YY`. |
| `title` | string ≤70 תווים | תיאור תצוגתי של שלב הלמידה הקרוב. |
| `learningUnitId` | string | ה-`id` של יחידת האם (הפניה בלבד — לא מכיל את המטא־דאטה שלה). |
| `componentPurpose` | enum | `instruction` / `practice` / `both`. |
| `isAssessment` | boolean | האם הרכיב הוא רכיב הערכה. |
| `manufacture` | string | שם ספק התוכן. עבור methodica: `"methodica"`. |
| `recommendedAfterFail` | array | מערך של רכיבים מומלצים לאחר כישלון ברכיב זה. |
| `isRequired` | boolean | האם יש חובת ביצוע. |
| `relativeDifficulty` | number 1-5 | קושי יחסי בתוך היחידה. |
| `masteryLevel` | enum | לא חובה בתשפ"ז. (basic / intermediate / advanced). |
| `order` | number | מיקום בסדר היחידה (1, 2, 3...). |
| `depthLevel` | enum | רמה ביחס לתכנית הלימודים. ראה רשימה למטה. |
| `cognitiveLevel` | enum | רמת חשיבה לפי מקצוע. ראה רשימות למטה. |
| `languages` | array | `["Hebrew"]` / `["Arabic"]` / `["English"]` — או שילוב. |
| `skills` | array | מיומנויות (בעבודה — לרוב `[]` בשלב זה). |
| `estimatedTimeInMinutes` | number | זמן מוערך. |
| `createdAt` | string | ISO 8601 (`YYYY-MM-DDTHH:MM:SS.SSSZ`). |
| `updatedAt` | string | ISO 8601. |
| `subContent` | array | מערך של פריטים (ראה שדות פריט). |

## שדות פריט תוכן

| שדה | סוג | תיאור |
|---|---|---|
| `id` | string | מזהה חד-חד־ערכי לכל פריט. תבנית: `<component-id>-ZZZ`. |
| `title` | string | כותרת חופשית של הפריט. |
| `informationToBot` | string | תיאור מובנה לבוט (ראה תבנית למטה). |
| `contentType` | enum | סוג התוכן. ראה רשימה למטה. |
| `mediaFormat` | enum | ערך יחיד. ראה רשימה למטה. |
| `questions` | array | מערך שאלות. ריק אם אין שאלה. |

### שדות של שאלה בודדת (בתוך `questions[]`)

| שדה | סוג | תיאור |
|---|---|---|
| `questionId` | string | מזהה פנימי (`q1`, `q2` וכו'). |
| `questionType` | enum | `fill-in` / `true-false` / `choice` / `numeric` / `sequencing` / `matching` / `other`. |
| `questionText` | string | נוסח השאלה כפי שמוצג ללומד. |
| `answers` | array/object | אפשרויות תשובה. מבנה שונה לפי `questionType`. |
| `correctAnswers` | array | תשובות נכונות. מבנה שונה לפי `questionType`. |

## רשימות סגורות

### contentType

| ערך | תיאור |
|---|---|
| `instruction` | הבנייה |
| `practice` | תרגול |
| `task-inquiry-or-project` | פרויקט או משימת חקר |
| `game-educational` | משחק לימודי |
| `text-reading` | ניתוח טקסט |
| `simulation` | סימולציה |
| `motivational` | פריט מוטיבציה (הוק, העשרה שאינה נבדקת) |
| `exercise-solved` | פתרון מודרך של תרגיל |
| `summary` | סיכום החומר |

### mediaFormat

`text` / `image` / `audio` / `video` / `animation` / `content-interactive` / `presentation`

**ערך יחיד בלבד**. פריט אינטראקטיבי שכולל וידאו כאחת האפשרויות הפנימיות → `content-interactive`.

### questionType

`fill-in` / `true-false` / `choice` / `numeric` / `sequencing` / `matching` / `other`.

### targetSector

`state-general` / `religious-state` / `orthodox` / `arab-sector` / `druze-sector` / `bedouin-sector` / `education-special`

### targetAudience

`general` / `excellent` / `populations-disadvantaged` / `immigrants-new` / `needs-special-with-students` / `gaps-language-with-students` / `at-risk-students`

### depthLevel

| ערך | תיאור |
|---|---|
| `basic-curriculum-core` | תוכנית לימודים בסיסית |
| `advanced-curriculum-core` | תוכנית לימודים העמקה |
| `enrichment-curriculum-core` | תוכנית לימודים העשרה |
| `basic-core-non` | לא חלק מהתוכנית הבסיסית |
| `advanced-core-non` | לא חלק מתוכנית ההעמקה |
| `enrichment-core-non` | לא חלק מתוכנית ההעשרה |

### cognitiveLevel — מתמטיקה

`knowledge-and-recall` / `thinking-algorithmic` / `process-thinking` / `reasoning-and-interpretation`

### cognitiveLevel — מדעים

`identifying` / `describing` / `information-retrieving` / `examples-providing` /
`making-connections` / `interpreting` / `applying-a-model-or-procedure` / `explaining` /
`providing-scientific-reasoning` / `analyzing` / `synthesizing` / `evaluating-and-justifying`

## תבנית `informationToBot`

מחרוזת אחת שמכילה ארבעה חלקים לפי סדר:

```
מטרת הפריט: <מה מטרת הפריט מבחינה פדגוגית>.
מה התלמיד אמור להבין/לתרגל: <תוכן ההבנה/יישום הצפוי>.
כיווני חשיבה ואסטרטגיות: <אילו אסטרטגיות פותרות את הפריט>.
טעויות נפוצות: <טעויות תלמידיות ידועות>.
מידע נוסף: <סוג האינטראקציה, רמזים, מסכים נוספים>. צילום מסך: לא צורף.
```

הבוט משתמש בזה כדי לעזור ללומד בזמן אמת — פרט מספיק שיהיה לו על מה להישען, אבל אל תפזר
מידע לא רלוונטי.

## דוגמת פלט JSON מלא

ראה `references/example-output.md` לדוגמאות ממשיות של קובצי יחידה ורכיב.
