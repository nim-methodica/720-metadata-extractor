# דוגמאות פלט JSON

מסמך זה נותן דוגמאות ממשיות של קובצי JSON לפי התקן V2.2. **כל שדה `id` הוא URL מלא**
לפי החוק ב-`conventions.md` (סעיף "פורמט ID"). הדוגמאות מתבססות על יחידות אמיתיות
(מתמטיקה — קנה מידה, מדעים — מדידת מסה).

## דוגמה 1: קובץ יחידה

`methodica-math-scale-01_unit.json`

```json
{
  "id": "https://lomdot.education.gov.il/metodica/720active/math/scale/01/",
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
  "prerequisiteLearningObjective": [
    "https://lomdot.education.gov.il/metodica/720active/math/proportion/05/"
  ]
}
```

## דוגמה 2: קובץ רכיב עם פריטים

`methodica-math-scale-01-01.json` (מקוצר — 2 פריטים לדוגמה)

```json
{
  "id": "https://lomdot.education.gov.il/metodica/720active/math/scale/01/methodica-math-scale-01-01/",
  "title": "הקנייה + תרגול חימום וסטנדרטי",
  "learningUnitId": "https://lomdot.education.gov.il/metodica/720active/math/scale/01/",
  "componentPurpose": "both",
  "isAssessment": false,
  "manufacture": "methodica",
  "recommendedAfterFail": [
    "https://lomdot.education.gov.il/metodica/720active/math/scale/01/methodica-math-scale-01-02/"
  ],
  "isRequired": true,
  "relativeDifficulty": 2,
  "order": 1,
  "depthLevel": "Core Curriculum Basic",
  "cognitiveLevel": "Process Thinking",
  "languages": ["Hebrew"],
  "skills": [],
  "estimatedTimeInMinutes": 24,
  "createdAt": "2026-07-08T00:00:00.000Z",
  "updatedAt": "2026-07-08T00:00:00.000Z",
  "subContent": [
    {
      "id": "https://lomdot.education.gov.il/metodica/720active/math/scale/01/methodica-math-scale-01-01/methodica-math-scale-01-01-001/",
      "title": "הוק - יחס רחפן והמציאות",
      "informationToBot": "מטרת הפריט: יצירת עניין ראשוני וחיבור הלומד למושג קנה מידה דרך הקשר של רחפן וצילום מגרש כדורגל. מה התלמיד אמור להבין: שיחס מספרי (כמו 10:1, 100:1, 1000:1) מאפשר 'לכווץ' מרחקים מהמציאות לתוך תצוגה קטנה. כיווני חשיבה ואסטרטגיות: התלמיד מתנסה בלחיצה ובוחר באיזה יחס יראה את החולצה של השחקן ובאיזה יחס יראה את המגרש כולו. טעויות נפוצות: אין הערכה בפריט - זהו פתיח מוטיבציוני. מידע נוסף: לפני התוכן הלימודי הלומד בוחר דמות מלווה ומקבל פתיח לקנה מידה. צילום מסך: לא צורף.",
      "contentType": "Motivational",
      "mediaFormat": "Interactive content",
      "questions": []
    },
    {
      "id": "https://lomdot.education.gov.il/metodica/720active/math/scale/01/methodica-math-scale-01-01/methodica-math-scale-01-01-006/",
      "title": "סטנדרטי 2: חדר ילדים - קנה מידה ומידות שטיח",
      "informationToBot": "מטרת הפריט: תרגול דו-שלבי - תחילה חישוב קנה מידה מנתונים בשתי יחידות שונות, ואחר כך שימוש בקנה המידה לחישוב מידות אובייקט בתרשים. מה התלמיד אמור להבין/לתרגל: סעיף א - בניית קנה מידה דורשת המרה ליחידה אחידה ואחר כך צמצום היחס. סעיף ב - לעבור מהמציאות לתרשים פירושו לחלק. טעויות נפוצות: שכחת המרת יחידות, חוסר צמצום, כפל במקום חילוק. מידע נוסף: שני סעיפים (א ו-ב). רמז זמין לכל סעיף. צילום מסך: לא צורף.",
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
          "questionText": "ב. נרצה לפרוס שטיח שמידותיו במציאות רוחב 1.8 מטרים ואורך 2.4 מטרים. מה יהיו מידות השטיח בתרשים?",
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

**שים לב** ש-`questionId` הוא **מזהה פנימי קצר** (`q1`, `q2`) — הוא לא URL. רק שדות
`id` ברמת יחידה/רכיב/פריט הם URLים מלאים.

## דוגמה 3: פריט משימת כיתה (ללא שאלה מוערכת)

```json
{
  "id": "https://lomdot.education.gov.il/metodica/720active/math/scale/01/methodica-math-scale-01-03/methodica-math-scale-01-03-001/",
  "title": "משימת כיתה - חישוב קנה מידה של מסלול",
  "informationToBot": "מטרת הפריט: יישום מציאותי של קנה מידה - מדידת מסלול אמיתי בשטח, חישוב אורכו, ובחירת קנה מידה. מה התלמיד אמור להבין/לתרגל: מדידה + הכפלה + בחירת קנה מידה מותאם. טעויות נפוצות: חישוב אורך צעד שגוי, אי-המרה, בחירת קנה מידה שלא 'נכנס' בדף. מידע נוסף: משימת חקר עם הוראות מפורטות + כלים נדרשים (סרגל, דף A4). צילום מסך: לא צורף.",
  "contentType": "Project or Inquiry Task",
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

## דוגמה 4: שאלת שיא רב-סעיפית (רכיב הערכה)

פריט אחד עם 4 שאלות ב-`questions[]`, ברכיב שמסומן `isAssessment: true`:

```json
{
  "id": "https://lomdot.education.gov.il/metodica/720active/science/mass-measure/01/methodica-science-mass-measure-01-05/methodica-science-mass-measure-01-05-001/",
  "title": "שאלת שיא: מדידת מסת גז (4 סעיפים)",
  "informationToBot": "מטרת הפריט: שאלת השיא של היחידה - תרחיש שלם של ניסוי מדעי המשלב את כל היכולות שנלמדו. תתי-סעיפים: א) ניסוי במערכת סגורה - זיהוי שימור מסה. ב) חישוב מסת גז בהפרש מדידות. ג) התאמת שיטת מדידה למטרת מחקר. ד) טיפול בתוצאות חריגות. ...",
  "contentType": "Project or Inquiry Task",
  "mediaFormat": "Interactive content",
  "questions": [
    {"questionId": "q1", "questionType": "choice", "questionText": "סעיף א: ...", "answers": [], "correctAnswers": []},
    {"questionId": "q2", "questionType": "choice", "questionText": "סעיף ב: ...", "answers": [], "correctAnswers": []},
    {"questionId": "q3", "questionType": "matching", "questionText": "סעיף ג: ...", "answers": {"source": [], "target": []}, "correctAnswers": []},
    {"questionId": "q4", "questionType": "choice", "questionText": "סעיף ד: ...", "answers": [], "correctAnswers": []}
  ]
}
```

הרכיב שמכיל את הפריט הזה צריך להיות מסומן `"isAssessment": true`.
