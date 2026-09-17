GOLD MACRO — AUTO UPDATE
========================

מה יש בחבילה?
--------------
index.html
data.json
scripts/update_data.py
.github/workflows/update-data.yml

כל הקבצים עובדים ללא API בתשלום וללא מפתח API.

העלאה ל-GitHub — הכי פשוט
--------------------------
1. פתח את repository בשם gold-macro.
2. לחץ Add file > Upload files.
3. חלץ את קובץ ה-ZIP במחשב.
4. גרור את כל התוכן של התיקייה gold-macro-auto ל-GitHub.
   חשוב: להעלות גם את התיקיות scripts ו-.github.
5. לחץ Commit changes.

אם GitHub לא מאפשר לגרור תיקייה שמתחילה בנקודה (.github):
-----------------------------------------------------------
אפשר להעלות דרך GitHub Desktop, או ליצור ידנית:
.github/workflows/update-data.yml

אחרי ההעלאה
------------
1. עבור ללשונית Actions.
2. פתח "Update Gold Macro Data".
3. לחץ Run workflow פעם אחת.
4. המתן בערך חצי דקה.
5. חזור לאתר ורענן.

לאחר מכן GitHub יריץ את העדכון אוטומטית פעם בשעה.

האתר:
https://benibenyosef.github.io/gold-macro/

מקורות חינמיים
---------------
- Metals Mine / Fair Economy weekly calendar JSON
- Forex Factory / Fair Economy fallback
- Federal Reserve / FRED לתשואות 2Y ו-10Y
- Stooq כ-fallback ל-DXY

הערה חשובה
-----------
DXY החינמי עלול להיות מושהה או לא זמין בחלק מהריצות.
אם מקור מסוים נכשל זמנית, שאר הנתונים עדיין יכולים להתעדכן.
אין בחבילה שירות בתשלום, מפתח API, כרטיס אשראי או מנוי.
