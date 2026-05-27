# דאשבורד מחקר אירוע: החלפת רואה חשבון מבקר

פרויקט אקדמי הבוחן באופן תיאורי את תגובת מחיר המניה סביב אירוע החלפת רואה חשבון מבקר בחברות ציבוריות בישראל, בדגש על מעברים בין Big-4 לבין משרדים שאינם Big-4.

המוצר הסופי להגשה הוא **דאשבורד Streamlit בעברית**. המחברות הן שכבת pipeline מחקרית והנדסית שמכינה נתונים נקיים, מזהים, מחירים ותוצאות אנליטיות עבור הדאשבורד.

## מגישים

- עומר טנא
- זיו אכד
- עדי קיכלר
- שחר אפק

## מבנה Pipeline

1. `01_data_intake_audit_and_source_feasibility.ipynb`  
   ניקוי נתונים, בדיקות איכות, הגדרת אירועים ובדיקת מקורות.

2. `02_ticker_mapping_and_source_resolution.ipynb`  
   מיפוי חברות לסימולי מסחר, מזהי TASE/ISIN וקובצי סקירה ידנית.

3. `03_price_extraction_and_event_windows.ipynb`  
   שליפת מחירי מניות ומדד ת״א 125, ובניית חלונות אירוע לפי ימי מסחר.

4. `04_event_study_returns_and_dashboard_tables.ipynb`  
   חישוב תשואת מניה, תשואת מדד, תשואה עודפת, סיכומים, חריגים וטבלאות מוכנות לדאשבורד.

5. `app/streamlit_app.py`  
   הדאשבורד האינטראקטיבי בעברית להצגת התוצאות, מסננים, תרשימים וייצוא לאקסל.

## הרצת הדאשבורד

מתיקיית הפרויקט:

```bash
pip install -r requirements.txt
streamlit run app/streamlit_app.py
```

הדאשבורד אינו שולף מחירים, אינו מחשב מחדש את הפייפליין ואינו משנה מיפוי סימולים. הוא טוען את הקבצים המוכנים מתוך:

```text
data/output/
reports/figures/
```

## קבצים מרכזיים לדאשבורד

- `data/output/event_study_results_v01.csv`
- `data/output/dashboard_summary_kpis_v01.json`
- `data/output/dashboard_switch_type_summary_v01.csv`
- `data/output/dashboard_outlier_report_v01.csv`
- `data/output/dashboard_exclusion_report_v01.csv`
- `data/output/dashboard_data_quality_summary_v01.csv`
- `data/output/dashboard_methodology_notes_v01.md`

## הערת מתודולוגיה

הדאשבורד מציג אינדיקציה תיאורית ראשונית בלבד. התוצאות אינן הוכחה סיבתית לכך שהחלפת רואה החשבון גרמה לתנועת מחיר מסוימת. נדרשות בדיקות המשך, בקרות ורובסטיות לצורך הסקה פורמלית.

## English Summary

This academic project builds a Hebrew Streamlit dashboard for a descriptive auditor-switch event study in Israeli public companies. The notebooks prepare the reproducible research pipeline; the final deliverable is the interactive dashboard.
