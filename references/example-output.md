# דוגמאות פלט JSON

מסמך זה נותן דוגמאות ממשיות של קובצי JSON לפי התקן, לצורך רפרנס. הדוגמאות מתבססות על
יחידות ממשיות שהופקו (מתמטיקה — קנה מידה, מדעים — מדידת מסה).

## דוגמה 1: קובץ יחידה

`methodica-math-scale-01_unit.json`

```json
{
  "id": "methodica-math-scale-01",
  "title": "יחידות מידה לצורך יישום יחס",
  "subTopic": "קנה מידה",
  "learningObjective": "יחידות מידה לצורך יישום יחס",
  "targetSector": [
    "State-General", "State-Religious", "Orthodox",
    "Arab Sector", "Druze Sector", "Bedouin Sector", "Special Education"
  ],
  "targetAudience": [
    "General", "Excellent", "Disadvantaged Populations",
    "New Immigrants", "Students with Special Needs",
    "Students with Language Gaps", "At Risk Students"
  ],
  "prerequisiteLearningObjective": ["methodica-math-proportion-05"]
}
```

## דוגמה 2: קובץ רכיב עם פריטים

`methodica-math-scale-01-01.json` (מקוצר — 2 פריטים לדוגמה)

```json
{
  "id": "methodica-math-scale-01-01",
  "title": "הקנייה + תרגול חימום וסטנדרטי",
  "learningUnitId": "methodica-math-scale-01",
  "componentPurpose": "both",
  "isAssessment": false,
  "manufacture": "methodica",
  "recommendedAfterFail": ["methodica-math-scale-01-02"],
  "isRequired": true,
  "relativeDifficulty": 2,
  "order": 1,
  "depthLevel": "Core Curriculum Basic",
  "cognitiveLevel": "Process Thinking",
  "languages": ["Hebrew"],
  "skills": [],
  "estimatedTimeInMinutes": 24,
  "createdAt": "2026-06-24T00:00:00.000Z",
  "updatedAt": "2026-06-24T00:00:00.000Z",
  "subContent": [
    {
      "id": "methodica-math-scale-01-01-001",
      "title": "הוק - יחס רחפן והמציאות",
      "informationToBot": "מטרת הפריט: יצירת עניין ראשוני וחיבור הלומד למושג קנה מידה דרך הקשר של רחפן וצילום מגרש כדורגל. מה התלמיד אמור להבין: שיחס מספרי (כמו 10:1, 100:1, 1000:1) מאפשר 'לכווץ' מרחקים מהמציאות לתוך תצוגה קטנה. כיווני חשיבה ואסטרטגיות: התלמיד מתנסה בלחיצה ובוחר באיזה יחס יראה את החולצה של השחקן ובאיזה יחס יראה את המגרש כולו. הקישור הוא חזותי - 'מה אני רואה' בכל יחס. טעויות נפוצות: אין הערכה בפריט - זהו פתיח מוטיבציוני. מידע נוסף: לפני התוכן הלימודי הלומד בוחר דמות מלווה ומקבל פתיח לקנה מידה דרך דוגמת רחפן מעל מגרש כדורגל ומפת עיר. צילום מסך: לא צורף.",
      "contentType": "Motivational",
      "mediaFormat": "Interactive content",
      "questions": []
    },
    {
      "id": "methodica-math-scale-01-01-006",
      "title": "סטנדרטי 2: חדר ילדים - קנה מידה ומידות שטיח",
      "informationToBot": "מטרת הפריט: תרגול דו-שלבי - תחילה חישוב קנה מידה מנתונים בשתי יחידות שונות, ואחר כך שימוש בקנה המידה לחישוב מידות אובייקט בתרשים. מה התלמיד אמור להבין/לתרגל: סעיף א - בניית קנה מידה דורשת המרה ליחידה אחידה ואחר כך צמצום היחס. סעיף ב - לעבור מהמציאות לתרשים פירושו לחלק. כיווני חשיבה ואסטרטגיות: סעיף א - 1.4 מטרים = 140 ס\"מ, היחס 140:7, צמצום ב-7 = 20:1. סעיף ב - מידות 1.8 ו-2.4 מטרים = 180 ו-240 ס\"מ; חילוק ב-20 = 9 ס\"מ × 12 ס\"מ. טעויות נפוצות: שכחת המרת יחידות, חוסר צמצום, כפל במקום חילוק, חישוב על מידה אחת בלבד. מידע נוסף: שני סעיפים (א ו-ב). רמז זמין לכל סעיף. צילום מסך: לא צורף.",
      "contentType": "Practice",
      "mediaFormat": "Interactive content",
      "questions": [
        {
          "questionId": "q1",
          "questionType": "numeric",
          "questionText": "א. אורך שולחן הכתיבה בתרשים הוא 7 ס\"מ, ובמציאות 1.4 מטרים. מהו קנה המידה של התרשים? (__ : 1)",
          "answers": [],
          "correctAnswers": [20]
        },
        {
          "questionId": "q2",
          "questionType": "choice",
          "questionText": "ב. נרצה לפרוס שטיח בצורת מלבן שמידותיו במציאות הן רוחב 1.8 מטרים ואורך 2.4 מטרים. מה יהיו מידות השטיח בתרשים?",
          "answers": [
            "רוחב 4.5 ס\"מ, אורך 6 ס\"מ",
            "רוחב 9 ס\"מ, אורך 12 ס\"מ",
            "רוחב 18 ס\"מ, אורך 24 ס\"מ",
            "רוחב 36 ס\"מ, אורך 48 ס\"מ"
          ],
          "correctAnswers": [
            "רוחב 9 ס\"מ, אורך 12 ס\"מ"
          ]
        }
      ]
    }
  ]
}
```

## דוגמה 3: פריט משימת כיתה (ללא שאלה)

```json
{
  "id": "methodica-math-scale-01-03-001",
  "title": "משימת כיתה - חישוב קנה מידה של מסלול",
  "informationToBot": "מטרת הפריט: יישום מציאותי של קנה מידה - מדידת מסלול אמיתי בשטח (חצר/בית ספר), חישוב אורכו במציאות, ובחירת קנה מידה לסרטוט במלואו על דף A4. מה התלמיד אמור להבין/לתרגל: מדידה בסביבה + הכפלת צעדים באורך + בחירת קנה מידה מותאם למרחב. כיווני חשיבה ואסטרטגיות: המשימה מתבצעת מחוץ למחשב במרחב הכיתה/בית הספר. הלומד יוצא, מודד, חוזר ומקליד את קנה המידה שחישב. טעויות נפוצות: חישוב אורך צעד שגוי, אי-המרה ליחידות אחידות, בחירת קנה מידה שלא 'נכנס' בדף. מידע נוסף: משימת חקר עם הוראות מפורטות + כלים נדרשים (סרגל, דף A4). צילום מסך: לא צורף.",
  "contentType": "Task Inquiry or Project",
  "mediaFormat": "Interactive content",
  "questions": [
    {
      "questionId": "q1",
      "questionType": "fill-in",
      "questionText": "אז מהו קנה המידה של המסלול שלכם? הקלידו אותו כאן.",
      "answers": [],
      "correctAnswers": []
    }
  ]
}
```

`correctAnswers` ריק — התשובה תלויה בביצוע הלומד ולא ניתן לוודא מראש.

## דוגמה 4: שאלת שיא רב-סעיפית

פריט אחד עם 4 שאלות ב-`questions[]`:

```json
{
  "id": "methodica-science-mass-measure-01-05-001",
  "title": "שאלת שיא: מדידת מסת גז (4 סעיפים)",
  "informationToBot": "מטרת הפריט: שאלת השיא של היחידה - תרחיש שלם של ניסוי מדעי המשלב את כל היכולות שנלמדו. תתי-סעיפים: א) ניסוי במערכת סגורה - זיהוי שימור מסה. ב) חישוב מסת גז בהפרש מדידות. ג) התאמת שיטת מדידה למטרת מחקר. ד) טיפול בתוצאות חריגות. ...",
  "contentType": "Task Inquiry or Project",
  "mediaFormat": "Interactive content",
  "questions": [
    {"questionId": "q1", "questionType": "choice", "questionText": "סעיף א: ...", "answers": [...], "correctAnswers": [...]},
    {"questionId": "q2", "questionType": "choice", "questionText": "סעיף ב: ...", "answers": [...], "correctAnswers": [...]},
    {"questionId": "q3", "questionType": "matching", "questionText": "סעיף ג: ...", "answers": {...}, "correctAnswers": [...]},
    {"questionId": "q4", "questionType": "choice", "questionText": "סעיף ד: ...", "answers": [...], "correctAnswers": [...]}
  ]
}
```

הרכיב שמכיל את הפריט הזה צריך להיות מסומן `"isAssessment": true`.
