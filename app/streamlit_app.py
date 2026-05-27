from __future__ import annotations

import json
import importlib.util
from datetime import date
from io import BytesIO
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st


st.set_page_config(
    page_title="דאשבורד מחקר אירוע - החלפת רואה חשבון מבקר",
    page_icon="📊",
    layout="wide",
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_OUTPUT_DIR = PROJECT_ROOT / "data" / "output"
FIGURES_DIR = PROJECT_ROOT / "reports" / "figures"

PATHS = {
    "results": DATA_OUTPUT_DIR / "event_study_results_v01.csv",
    "kpis_csv": DATA_OUTPUT_DIR / "dashboard_summary_kpis_v01.csv",
    "kpis_json": DATA_OUTPUT_DIR / "dashboard_summary_kpis_v01.json",
    "switch_summary": DATA_OUTPUT_DIR / "dashboard_switch_type_summary_v01.csv",
    "top_positive": DATA_OUTPUT_DIR / "dashboard_top_positive_reactions_v01.csv",
    "top_negative": DATA_OUTPUT_DIR / "dashboard_top_negative_reactions_v01.csv",
    "exclusion_report": DATA_OUTPUT_DIR / "dashboard_exclusion_report_v01.csv",
    "data_quality": DATA_OUTPUT_DIR / "dashboard_data_quality_summary_v01.csv",
    "outlier_report": DATA_OUTPUT_DIR / "dashboard_outlier_report_v01.csv",
    "statistical_summary": DATA_OUTPUT_DIR / "exploratory_statistical_summary_v01.csv",
    "methodology": DATA_OUTPUT_DIR / "dashboard_methodology_notes_v01.md",
}


HEBREW_COLUMNS = {
    "event_id": "מזהה אירוע",
    "company_name": "שם חברה",
    "switch_type": "סוג מעבר",
    "event_date_basis": "בסיס תאריך אירוע",
    "event_date": "תאריך אירוע",
    "yahoo_ticker": "סימול Yahoo",
    "mapping_status": "סטטוס מיפוי",
    "mapping_confidence": "רמת ביטחון במיפוי",
    "stock_t_minus_5_date": "תאריך מניה t-5",
    "stock_event_trading_date": "תאריך מסחר באירוע",
    "stock_t_plus_5_date": "תאריך מניה t+5",
    "market_t_minus_5_date": "תאריך מדד t-5",
    "market_event_trading_date": "תאריך מדד באירוע",
    "market_t_plus_5_date": "תאריך מדד t+5",
    "stock_price_t_minus_5": "מחיר מניה t-5",
    "stock_price_event": "מחיר מניה ביום האירוע",
    "stock_price_t_plus_5": "מחיר מניה t+5",
    "ta125_price_t_minus_5": "מחיר ת״א 125 t-5",
    "ta125_price_event": "מחיר ת״א 125 ביום האירוע",
    "ta125_price_t_plus_5": "מחיר ת״א 125 t+5",
    "price_status": "סטטוס מחיר מניה",
    "market_price_status": "סטטוס מדד",
    "analysis_eligible": "נכלל בחישוב",
    "analysis_exclusion_reason": "סיבת החרגה",
    "price_notes": "הערות מחיר מניה",
    "market_price_notes": "הערות מדד",
    "stock_return": "תשואת מניה",
    "ta125_return": "תשואת ת״א 125",
    "market_adjusted_return": "תשואה עודפת",
    "stock_return_pct": "תשואת מניה (%)",
    "ta125_return_pct": "תשואת ת״א 125 (%)",
    "market_adjusted_return_pct": "תשואה עודפת (%)",
    "stock_event_day_position_pct": "מיקום מניה ביום האירוע (%)",
    "ta125_event_day_position_pct": "מיקום מדד ביום האירוע (%)",
    "market_adjusted_event_day_position_pct": "מיקום עודף ביום האירוע (%)",
    "reaction_direction": "כיוון תגובה",
    "absolute_market_adjusted_return": "ערך מוחלט של תשואה עודפת",
    "is_extreme_market_adjusted_return_20pct": "חריג 20%",
    "is_extreme_market_adjusted_return_50pct": "חריג 50%",
    "outlier_note": "הערת חריג",
    "total_events": "סך אירועים",
    "eligible_events": "אירועים שנכללו",
    "excluded_events": "אירועים שהוחרגו",
    "eligibility_rate": "שיעור הכללה",
    "mean_stock_return_pct": "ממוצע תשואת מניה (%)",
    "mean_ta125_return_pct": "ממוצע תשואת ת״א 125 (%)",
    "mean_market_adjusted_return_pct": "ממוצע תשואה עודפת (%)",
    "mean_market_adjusted_return_excluding_20pct_outliers_pct": "ממוצע ללא חריגי 20% (%)",
    "number_of_20pct_outliers": "מספר חריגי 20%",
    "number_of_50pct_outliers": "מספר חריגי 50%",
    "positive_reactions_count": "תגובות חיוביות",
    "negative_reactions_count": "תגובות שליליות",
    "neutral_reactions_count": "תגובות ניטרליות",
    "count": "כמות",
    "percentage_of_total_events": "אחוז מכלל האירועים",
    "metric": "מדד",
    "value": "ערך",
    "interpretation": "פירוש",
}


DISPLAY_RESULT_COLUMNS = [
    "company_name",
    "switch_type",
    "event_date",
    "yahoo_ticker",
    "stock_return_pct",
    "ta125_return_pct",
    "market_adjusted_return_pct",
    "reaction_direction",
    "analysis_eligible",
    "analysis_exclusion_reason",
    "price_status",
    "market_price_status",
    "outlier_note",
]


def inject_css() -> None:
    st.markdown(
        """
        <style>
        html, body, [class*="css"] {
            direction: rtl;
            text-align: right;
            font-family: "Segoe UI", "Arial", sans-serif;
            color: #111827;
            background: #f8fafc;
        }
        .main .block-container {
            padding-top: 1.5rem;
            max-width: 1500px;
        }
        h1, h2, h3, h4 {
            color: #0f172a;
            letter-spacing: 0;
        }
        p, li, label, span, div {
            font-size: 1rem;
        }
        .hero-box {
            background: #ffffff;
            border: 1px solid #cbd5e1;
            box-shadow: 0 2px 10px rgba(15, 23, 42, 0.08);
            border-radius: 8px;
            padding: 1.25rem 1.4rem;
            margin-bottom: 1rem;
        }
        .hero-box h1 {
            color: #0f172a !important;
            font-size: 2.2rem;
            font-weight: 800;
            line-height: 1.25;
            margin-bottom: 0.65rem;
        }
        .hero-box p {
            color: #1f2937 !important;
            font-size: 1.08rem;
            font-weight: 500;
            line-height: 1.65;
            margin-bottom: 0.75rem;
        }
        .submitters {
            font-weight: 700;
            color: #1e3a8a !important;
            margin-top: 0.75rem;
        }
        .academic-note {
            background: #fff7ed;
            border-right: 5px solid #ea580c;
            color: #7c2d12 !important;
            padding: 0.85rem 1rem;
            border-radius: 6px;
            margin-top: 0.8rem;
            font-weight: 600;
        }
        .academic-note, .academic-note * {
            color: #7c2d12 !important;
        }
        .kpi-card {
            background: #ffffff;
            border: 1px solid #94a3b8;
            box-shadow: 0 1px 8px rgba(15, 23, 42, 0.10);
            border-radius: 8px;
            padding: 1rem;
            min-height: 112px;
        }
        .kpi-label {
            color: #334155;
            font-size: 0.92rem;
            font-weight: 700;
            margin-bottom: 0.35rem;
        }
        .kpi-value {
            color: #0f172a;
            font-size: 1.65rem;
            font-weight: 800;
            line-height: 1.2;
        }
        .small-caption {
            color: #475569;
            font-size: 0.92rem;
        }
        div[data-testid="stDataFrame"] {
            direction: ltr;
        }
        .stAlert {
            direction: rtl;
            text-align: right;
        }
        button, .stDownloadButton button {
            font-weight: 700;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def show_missing_file_warning(path: Path) -> None:
    st.warning(f"⚠️ הקובץ לא נמצא ולכן רכיב זה לא יוצג: `{path.as_posix()}`")


@st.cache_data(show_spinner=False)
def load_csv_safe(path_str: str) -> pd.DataFrame:
    path = Path(path_str)
    if not path.exists():
        return pd.DataFrame()
    try:
        return pd.read_csv(path, encoding="utf-8-sig")
    except Exception as exc:
        st.warning(f"לא ניתן לטעון את הקובץ `{path.name}`: {exc}")
        return pd.DataFrame()


@st.cache_data(show_spinner=False)
def load_json_safe(path_str: str) -> dict[str, Any]:
    path = Path(path_str)
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        st.warning(f"לא ניתן לטעון את קובץ ה-JSON `{path.name}`: {exc}")
        return {}


@st.cache_data(show_spinner=False)
def load_markdown_safe(path_str: str) -> str:
    path = Path(path_str)
    if not path.exists():
        return ""
    try:
        return path.read_text(encoding="utf-8")
    except Exception as exc:
        st.warning(f"לא ניתן לטעון את קובץ המתודולוגיה `{path.name}`: {exc}")
        return ""


def to_bool_series(series: pd.Series) -> pd.Series:
    if series.dtype == bool:
        return series.fillna(False)
    return series.astype(str).str.lower().isin(["true", "1", "yes", "כן"])


def prepare_results_df(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
    prepared = df.copy()
    for col in ["event_date", "stock_t_minus_5_date", "stock_event_trading_date", "stock_t_plus_5_date"]:
        if col in prepared.columns:
            prepared[col] = pd.to_datetime(prepared[col], errors="coerce")
    for col in [
        "stock_return_pct",
        "ta125_return_pct",
        "market_adjusted_return_pct",
        "mean_market_adjusted_return_pct",
    ]:
        if col in prepared.columns:
            prepared[col] = pd.to_numeric(prepared[col], errors="coerce")
    for col in ["analysis_eligible", "is_extreme_market_adjusted_return_20pct", "is_extreme_market_adjusted_return_50pct"]:
        if col in prepared.columns:
            prepared[col] = to_bool_series(prepared[col])
    return prepared


def format_pct(value: Any) -> str:
    if value is None or pd.isna(value):
        return "לא זמין"
    try:
        return f"{float(value) * 100:.2f}%"
    except Exception:
        return "לא זמין"


def format_pct_from_pct_value(value: Any) -> str:
    if value is None or pd.isna(value):
        return "לא זמין"
    try:
        return f"{float(value):.2f}%"
    except Exception:
        return "לא זמין"


def format_number(value: Any) -> str:
    if value is None or pd.isna(value):
        return "לא זמין"
    try:
        return f"{float(value):,.0f}"
    except Exception:
        return str(value)


def render_kpi(label: str, value: str) -> None:
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{value}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def rename_columns_hebrew(df: pd.DataFrame) -> pd.DataFrame:
    return df.rename(columns={col: HEBREW_COLUMNS.get(col, col) for col in df.columns})


def safe_plotly_chart(fig: Any, message: str = "לא ניתן להציג תרשים זה.") -> None:
    if fig is None:
        st.warning(message)
        return
    try:
        st.plotly_chart(fig, use_container_width=True, config={"displaylogo": False})
    except Exception as exc:
        st.warning(f"{message} שגיאה: {exc}")


def apply_filters(
    df: pd.DataFrame,
    selected_switch_types: list[str],
    selected_reactions: list[str],
    eligibility_filter: str,
    outlier_filter: str,
    date_range: tuple[date, date] | None,
    search_text: str,
) -> pd.DataFrame:
    if df.empty:
        return df
    filtered = df.copy()

    if selected_switch_types and "switch_type" in filtered.columns:
        filtered = filtered[filtered["switch_type"].isin(selected_switch_types)]

    if selected_reactions and "reaction_direction" in filtered.columns:
        filtered = filtered[filtered["reaction_direction"].isin(selected_reactions)]

    if "analysis_eligible" in filtered.columns:
        if eligibility_filter == "אירועים שנכללו בחישוב בלבד":
            filtered = filtered[filtered["analysis_eligible"]]
        elif eligibility_filter == "אירועים שהוחרגו בלבד":
            filtered = filtered[~filtered["analysis_eligible"]]

    if "is_extreme_market_adjusted_return_20pct" in filtered.columns:
        if outlier_filter == "להחריג תצפיות חריגות מעל 20%":
            filtered = filtered[~filtered["is_extreme_market_adjusted_return_20pct"]]
        elif outlier_filter == "להציג חריגים בלבד":
            filtered = filtered[filtered["is_extreme_market_adjusted_return_20pct"]]

    if date_range and "event_date" in filtered.columns and len(date_range) == 2:
        start_date, end_date = date_range
        event_dates = pd.to_datetime(filtered["event_date"], errors="coerce")
        filtered = filtered[(event_dates.dt.date >= start_date) & (event_dates.dt.date <= end_date)]

    if search_text and "company_name" in filtered.columns:
        filtered = filtered[filtered["company_name"].astype(str).str.contains(search_text, case=False, na=False)]

    return filtered


def create_excel_download(df: pd.DataFrame, filename: str) -> bytes:
    buffer = BytesIO()
    engine = "xlsxwriter" if importlib.util.find_spec("xlsxwriter") else "openpyxl"
    with pd.ExcelWriter(buffer, engine=engine) as writer:
        rename_columns_hebrew(df).to_excel(writer, sheet_name="Filtered Results", index=False)
    buffer.seek(0)
    return buffer.getvalue()


def write_sheet(writer: pd.ExcelWriter, sheet_name: str, df: pd.DataFrame) -> None:
    if df is None or df.empty:
        pd.DataFrame({"הודעה": ["אין נתונים זמינים"]}).to_excel(writer, sheet_name=sheet_name[:31], index=False)
    else:
        rename_columns_hebrew(df).to_excel(writer, sheet_name=sheet_name[:31], index=False)


def create_full_dashboard_excel_export(
    filtered_results: pd.DataFrame,
    kpis_df: pd.DataFrame,
    switch_summary_df: pd.DataFrame,
    top_positive_df: pd.DataFrame,
    top_negative_df: pd.DataFrame,
    outlier_report_df: pd.DataFrame,
    exclusion_report_df: pd.DataFrame,
    data_quality_df: pd.DataFrame,
    statistical_summary_df: pd.DataFrame,
) -> bytes:
    buffer = BytesIO()
    engine = "xlsxwriter" if importlib.util.find_spec("xlsxwriter") else "openpyxl"
    with pd.ExcelWriter(buffer, engine=engine) as writer:
        write_sheet(writer, "Filtered Results", filtered_results)
        write_sheet(writer, "Summary KPIs", kpis_df)
        write_sheet(writer, "Switch Type Summary", switch_summary_df)
        write_sheet(writer, "Top Positive Reactions", top_positive_df)
        write_sheet(writer, "Top Negative Reactions", top_negative_df)
        write_sheet(writer, "Outlier Report", outlier_report_df)
        write_sheet(writer, "Exclusion Report", exclusion_report_df)
        write_sheet(writer, "Data Quality Summary", data_quality_df)
        if statistical_summary_df is not None and not statistical_summary_df.empty:
            write_sheet(writer, "Statistical Summary", statistical_summary_df)
    buffer.seek(0)
    return buffer.getvalue()


def calculate_switch_summary(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty or "switch_type" not in df.columns:
        return pd.DataFrame()
    rows = []
    for switch_type, group in df.groupby("switch_type", dropna=False):
        eligible = group[group.get("analysis_eligible", False)]
        robust = eligible[~eligible.get("is_extreme_market_adjusted_return_20pct", False)]
        rows.append(
            {
                "switch_type": switch_type,
                "total_events": len(group),
                "eligible_events": int(group.get("analysis_eligible", pd.Series(False, index=group.index)).sum()),
                "excluded_events": int((~group.get("analysis_eligible", pd.Series(False, index=group.index))).sum()),
                "mean_market_adjusted_return_pct": eligible["market_adjusted_return_pct"].mean() if "market_adjusted_return_pct" in eligible else np.nan,
                "mean_market_adjusted_return_excluding_20pct_outliers_pct": robust["market_adjusted_return_pct"].mean()
                if "market_adjusted_return_pct" in robust
                else np.nan,
                "positive_reactions_count": int(eligible.get("reaction_direction", pd.Series(index=eligible.index)).eq("Positive").sum()),
                "negative_reactions_count": int(eligible.get("reaction_direction", pd.Series(index=eligible.index)).eq("Negative").sum()),
                "neutral_reactions_count": int(eligible.get("reaction_direction", pd.Series(index=eligible.index)).eq("Neutral").sum()),
            }
        )
    return pd.DataFrame(rows)


def main() -> None:
    inject_css()

    results_df = prepare_results_df(load_csv_safe(str(PATHS["results"])))
    kpis_df = load_csv_safe(str(PATHS["kpis_csv"]))
    kpis_json = load_json_safe(str(PATHS["kpis_json"]))
    switch_summary_df = load_csv_safe(str(PATHS["switch_summary"]))
    top_positive_df = load_csv_safe(str(PATHS["top_positive"]))
    top_negative_df = load_csv_safe(str(PATHS["top_negative"]))
    exclusion_report_df = load_csv_safe(str(PATHS["exclusion_report"]))
    data_quality_df = load_csv_safe(str(PATHS["data_quality"]))
    outlier_report_df = load_csv_safe(str(PATHS["outlier_report"]))
    statistical_summary_df = load_csv_safe(str(PATHS["statistical_summary"]))
    methodology_notes = load_markdown_safe(str(PATHS["methodology"]))

    st.markdown(
        """
        <div class="hero-box">
            <h1>דאשבורד מחקר אירוע: החלפת רואה חשבון מבקר</h1>
            <p>בחינה תיאורית של תגובת מחיר המניה סביב אירוע החלפת רואה חשבון מבקר בחברות ציבוריות בישראל</p>
            <div class="submitters">מגישים: עומר טנא, זיו אכד, עדי קיכלר, שחר אפק</div>
            <div class="academic-note">הדאשבורד מציג אינדיקציה תיאורית ראשונית בלבד ואינו מהווה הוכחה סיבתית.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    for key in ["results", "kpis_csv", "switch_summary", "methodology"]:
        if not PATHS[key].exists():
            show_missing_file_warning(PATHS[key])

    if results_df.empty:
        st.error("לא ניתן להציג את הדאשבורד משום שקובץ תוצאות מחקר האירוע חסר או ריק.")
        return

    st.sidebar.header("מסננים")
    switch_options = ["Big to Small", "Small to Big", "Big to Big", "Small to Small", "Unknown"]
    present_switches = sorted(results_df.get("switch_type", pd.Series(dtype=str)).dropna().astype(str).unique().tolist())
    full_switch_options = [option for option in switch_options if option in present_switches] + [
        option for option in present_switches if option not in switch_options
    ]
    selected_switch_types = st.sidebar.multiselect("סוג מעבר רו״ח", full_switch_options, default=full_switch_options)

    reaction_options = ["Positive", "Negative", "Neutral", "Not calculated"]
    present_reactions = sorted(results_df.get("reaction_direction", pd.Series(dtype=str)).dropna().astype(str).unique().tolist())
    full_reaction_options = [option for option in reaction_options if option in present_reactions] + [
        option for option in present_reactions if option not in reaction_options
    ]
    selected_reactions = st.sidebar.multiselect("כיוון תגובה", full_reaction_options, default=full_reaction_options)

    eligibility_filter = st.sidebar.radio(
        "סטטוס הכללה",
        ["כל האירועים", "אירועים שנכללו בחישוב בלבד", "אירועים שהוחרגו בלבד"],
        index=0,
    )
    outlier_filter = st.sidebar.radio(
        "טיפול בחריגים",
        ["להציג הכל", "להחריג תצפיות חריגות מעל 20%", "להציג חריגים בלבד"],
        index=0,
    )

    event_dates = pd.to_datetime(results_df.get("event_date"), errors="coerce").dropna()
    if not event_dates.empty:
        min_date = event_dates.min().date()
        max_date = event_dates.max().date()
        date_range = st.sidebar.date_input("טווח תאריכים לפי תאריך אירוע", value=(min_date, max_date), min_value=min_date, max_value=max_date)
        if isinstance(date_range, tuple) and len(date_range) == 2:
            selected_date_range = date_range
        else:
            selected_date_range = (min_date, max_date)
    else:
        selected_date_range = None
        st.sidebar.warning("אין תאריכי אירוע תקינים לסינון.")

    search_text = st.sidebar.text_input("חיפוש חברה לפי טקסט", value="")

    filtered_df = apply_filters(
        results_df,
        selected_switch_types,
        selected_reactions,
        eligibility_filter,
        outlier_filter,
        selected_date_range,
        search_text.strip(),
    )
    filtered_eligible_df = filtered_df[filtered_df.get("analysis_eligible", False)] if "analysis_eligible" in filtered_df else pd.DataFrame()
    filtered_switch_summary_df = calculate_switch_summary(filtered_df)

    tab_overview, tab_results, tab_switch, tab_outliers, tab_quality, tab_methodology, tab_export = st.tabs(
        [
            "סקירה כללית",
            "תוצאות מחקר האירוע",
            "ניתוח לפי סוג מעבר",
            "חריגים ורגישות",
            "החרגות ואיכות נתונים",
            "מתודולוגיה",
            "ייצוא נתונים",
        ]
    )

    with tab_overview:
        st.subheader("סקירה כללית")
        st.write(
            "הדאשבורד מציג תוצאות תיאוריות מחלון אירוע של חמישה ימי מסחר לפני ועד חמישה ימי מסחר אחרי אירוע החלפת רואה החשבון המבקר."
        )

        kpi_cols = st.columns(4)
        kpi_items = [
            ("סך אירועים", format_number(kpis_json.get("total_events", len(results_df)))),
            ("אירועים שנכללו בחישוב", format_number(kpis_json.get("analysis_eligible_events", results_df.get("analysis_eligible", pd.Series()).sum()))),
            ("אירועים שהוחרגו", format_number(kpis_json.get("excluded_events", len(results_df) - results_df.get("analysis_eligible", pd.Series(dtype=bool)).sum()))),
            ("ממוצע תשואת מניה", format_pct(kpis_json.get("mean_stock_return"))),
            ("ממוצע תשואת ת״א 125", format_pct(kpis_json.get("mean_ta125_return"))),
            ("ממוצע תשואה עודפת", format_pct(kpis_json.get("mean_market_adjusted_return"))),
            ("ממוצע תשואה עודפת ללא חריגי 20%", format_pct(kpis_json.get("mean_market_adjusted_return_excluding_20pct_outliers"))),
            ("תגובות חיוביות", format_number(kpis_json.get("positive_reactions_count"))),
            ("תגובות שליליות", format_number(kpis_json.get("negative_reactions_count"))),
            ("תגובות ניטרליות", format_number(kpis_json.get("neutral_reactions_count"))),
            ("חריגי 20%", format_number(kpis_json.get("number_of_20pct_outliers"))),
            ("חריגי 50%", format_number(kpis_json.get("number_of_50pct_outliers"))),
        ]
        for idx, (label, value) in enumerate(kpi_items):
            with kpi_cols[idx % 4]:
                render_kpi(label, value)

        st.markdown('<div class="academic-note">הדאשבורד מציג אינדיקציה תיאורית בלבד; אין לפרש את התוצאות כהוכחה סיבתית.</div>', unsafe_allow_html=True)

        chart_col1, chart_col2 = st.columns(2)
        with chart_col1:
            st.subheader("התפלגות תשואה עודפת")
            if "market_adjusted_return_pct" in filtered_eligible_df.columns and not filtered_eligible_df.empty:
                fig = px.histogram(
                    filtered_eligible_df,
                    x="market_adjusted_return_pct",
                    nbins=14,
                    labels={"market_adjusted_return_pct": "תשואה עודפת (%)"},
                    title="התפלגות תשואה עודפת בקרב אירועים שנכללו",
                )
                safe_plotly_chart(fig)
            else:
                st.warning("אין מספיק נתונים להצגת התפלגות תשואה עודפת.")
        with chart_col2:
            st.subheader("תשואת מניה מול תשואת מדד")
            required = {"stock_return_pct", "ta125_return_pct"}
            if required.issubset(filtered_eligible_df.columns) and not filtered_eligible_df.empty:
                fig = px.scatter(
                    filtered_eligible_df,
                    x="ta125_return_pct",
                    y="stock_return_pct",
                    color="switch_type" if "switch_type" in filtered_eligible_df.columns else None,
                    hover_name="company_name" if "company_name" in filtered_eligible_df.columns else None,
                    labels={
                        "ta125_return_pct": "תשואת ת״א 125 (%)",
                        "stock_return_pct": "תשואת מניה (%)",
                        "switch_type": "סוג מעבר",
                    },
                    title="תשואת מניה מול תשואת ת״א 125",
                )
                safe_plotly_chart(fig)
            else:
                st.warning("אין מספיק נתונים להצגת פיזור תשואות.")

        st.subheader("תצוגה מקדימה של תוצאות מסוננות שנכללו בחישוב")
        preview_columns = [col for col in DISPLAY_RESULT_COLUMNS if col in filtered_eligible_df.columns]
        st.dataframe(rename_columns_hebrew(filtered_eligible_df[preview_columns].head(20)), use_container_width=True, hide_index=True)

    with tab_results:
        st.subheader("תוצאות מחקר האירוע")
        st.write("הטבלה כוללת את התוצאות לאחר החלת המסננים הנוכחיים. שורות שהוחרגו נשמרות ומוצגות עם סיבת החרגה.")
        display_columns = [col for col in DISPLAY_RESULT_COLUMNS if col in filtered_df.columns]
        if display_columns:
            st.dataframe(rename_columns_hebrew(filtered_df[display_columns]), use_container_width=True, hide_index=True)
        else:
            st.warning("אין עמודות זמינות להצגת טבלת התוצאות.")
        st.download_button(
            "הורדת הטבלה המסוננת לאקסל",
            data=create_excel_download(filtered_df, "filtered_event_study_results.xlsx"),
            file_name="filtered_event_study_results.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

    with tab_switch:
        st.subheader("ניתוח לפי סוג מעבר")
        st.write("ההשוואה לפי סוג מעבר היא תיאורית בלבד ועלולה להיות מושפעת מגודל מדגם, חריגים, מאפייני חברה ואירועים מקבילים.")
        if not filtered_switch_summary_df.empty:
            st.dataframe(rename_columns_hebrew(filtered_switch_summary_df), use_container_width=True, hide_index=True)
            chart_a, chart_b = st.columns(2)
            with chart_a:
                if "mean_market_adjusted_return_pct" in filtered_switch_summary_df.columns:
                    fig = px.bar(
                        filtered_switch_summary_df,
                        x="switch_type",
                        y="mean_market_adjusted_return_pct",
                        labels={"switch_type": "סוג מעבר", "mean_market_adjusted_return_pct": "ממוצע תשואה עודפת (%)"},
                        title="ממוצע תשואה עודפת לפי סוג מעבר",
                    )
                    safe_plotly_chart(fig)
            with chart_b:
                if "mean_market_adjusted_return_excluding_20pct_outliers_pct" in filtered_switch_summary_df.columns:
                    fig = px.bar(
                        filtered_switch_summary_df,
                        x="switch_type",
                        y="mean_market_adjusted_return_excluding_20pct_outliers_pct",
                        labels={
                            "switch_type": "סוג מעבר",
                            "mean_market_adjusted_return_excluding_20pct_outliers_pct": "ממוצע ללא חריגי 20% (%)",
                        },
                        title="ממוצע תשואה עודפת ללא חריגי 20%",
                    )
                    safe_plotly_chart(fig)

            count_col, reaction_col = st.columns(2)
            with count_col:
                fig = px.bar(
                    filtered_switch_summary_df,
                    x="switch_type",
                    y="eligible_events",
                    labels={"switch_type": "סוג מעבר", "eligible_events": "אירועים שנכללו"},
                    title="מספר אירועים שנכללו לפי סוג מעבר",
                )
                safe_plotly_chart(fig)
            with reaction_col:
                reaction_cols = [
                    col
                    for col in ["positive_reactions_count", "negative_reactions_count", "neutral_reactions_count"]
                    if col in filtered_switch_summary_df.columns
                ]
                if reaction_cols:
                    melted = filtered_switch_summary_df.melt(
                        id_vars="switch_type",
                        value_vars=reaction_cols,
                        var_name="כיוון תגובה",
                        value_name="כמות",
                    )
                    fig = px.bar(
                        melted,
                        x="switch_type",
                        y="כמות",
                        color="כיוון תגובה",
                        barmode="group",
                        labels={"switch_type": "סוג מעבר"},
                        title="תגובות לפי סוג מעבר",
                    )
                    safe_plotly_chart(fig)
        else:
            st.warning("אין נתונים זמינים לניתוח לפי סוג מעבר לאחר המסננים.")

    with tab_outliers:
        st.subheader("חריגים ורגישות")
        st.write("תצפיות חריגות אינן נמחקות מהתוצאה הראשית, אך מוצגות בנפרד לצורך שקיפות וניתוח רגישות.")
        cols = st.columns(4)
        with cols[0]:
            render_kpi("חריגי 20%", format_number(kpis_json.get("number_of_20pct_outliers")))
        with cols[1]:
            render_kpi("חריגי 50%", format_number(kpis_json.get("number_of_50pct_outliers")))
        with cols[2]:
            render_kpi("ממוצע ראשי", format_pct(kpis_json.get("mean_market_adjusted_return")))
        with cols[3]:
            render_kpi("ממוצע ללא חריגי 20%", format_pct(kpis_json.get("mean_market_adjusted_return_excluding_20pct_outliers")))

        if not outlier_report_df.empty:
            st.dataframe(rename_columns_hebrew(outlier_report_df), use_container_width=True, hide_index=True)
        else:
            show_missing_file_warning(PATHS["outlier_report"])

        if "market_adjusted_return_pct" in filtered_eligible_df.columns and not filtered_eligible_df.empty:
            fig = px.box(
                filtered_eligible_df,
                y="market_adjusted_return_pct",
                points="all",
                labels={"market_adjusted_return_pct": "תשואה עודפת (%)"},
                title="תרשים קופסה של תשואה עודפת",
            )
            safe_plotly_chart(fig)
        else:
            st.warning("אין מספיק נתונים להצגת תרשים קופסה.")

    with tab_quality:
        st.subheader("החרגות ואיכות נתונים")
        st.write("שורות שהוחרגו נשמרות בדאטה אך אינן נכללות בחישוב התשואות.")
        if not exclusion_report_df.empty:
            st.dataframe(rename_columns_hebrew(exclusion_report_df), use_container_width=True, hide_index=True)
        else:
            show_missing_file_warning(PATHS["exclusion_report"])

        status_col1, status_col2 = st.columns(2)
        with status_col1:
            if "price_status" in filtered_df.columns:
                status_counts = filtered_df["price_status"].value_counts(dropna=False).reset_index()
                status_counts.columns = ["סטטוס מחיר מניה", "כמות"]
                fig = px.bar(status_counts, x="סטטוס מחיר מניה", y="כמות", title="התפלגות סטטוס מחיר מניה")
                safe_plotly_chart(fig)
        with status_col2:
            if "market_price_status" in filtered_df.columns:
                market_counts = filtered_df["market_price_status"].fillna("לא רלוונטי").value_counts(dropna=False).reset_index()
                market_counts.columns = ["סטטוס מדד", "כמות"]
                fig = px.bar(market_counts, x="סטטוס מדד", y="כמות", title="התפלגות סטטוס מדד")
                safe_plotly_chart(fig)

        st.subheader("סיכום איכות נתונים")
        if not data_quality_df.empty:
            st.dataframe(rename_columns_hebrew(data_quality_df), use_container_width=True, hide_index=True)
        else:
            show_missing_file_warning(PATHS["data_quality"])

    with tab_methodology:
        st.subheader("מתודולוגיה")
        st.markdown(
            """
            **חלון אירוע:** t-5 עד t+5 ימי מסחר  
            **מדד ייחוס:** ת״א 125  
            **כלל תאריך מסחר:** אם אין מסחר ביום האירוע, נעשה שימוש ביום המסחר הקרוב לאחר תאריך האירוע.

            **תשואת מניה:**  
            `stock_return = stock_price_t_plus_5 / stock_price_t_minus_5 - 1`

            **תשואת מדד ת״א 125:**  
            `ta125_return = ta125_price_t_plus_5 / ta125_price_t_minus_5 - 1`

            **תשואה עודפת:**  
            `market_adjusted_return = stock_return - ta125_return`

            **טיפול בחריגים:** התוצאות הראשיות כוללות את כל האירועים שנכללו בחישוב. בנוסף מוצגים מדדי רגישות ללא תצפיות שבהן הערך המוחלט של התשואה העודפת גבוה מ-20%.

            **מגבלות:** הניתוח תיאורי בלבד. יש לבחון מיפוי סימולים, פעולות תאגידיות, נזילות, אירועים מקבילים ותאריכי אירוע לפני הסקת מסקנות מחקריות.
            """
        )
        if methodology_notes:
            with st.expander("הערות מתודולוגיות מתוך קובץ הפייפליין"):
                st.markdown(methodology_notes)
        else:
            show_missing_file_warning(PATHS["methodology"])

    with tab_export:
        st.subheader("ייצוא נתונים")
        st.write("הייצוא משקף את המסננים הפעילים עבור גיליון התוצאות המסוננות.")
        filtered_excel = create_excel_download(filtered_df, "filtered_event_study_results.xlsx")
        full_excel = create_full_dashboard_excel_export(
            filtered_results=filtered_df,
            kpis_df=dashboard_summary_kpis_df_from_json(kpis_json, kpis_df),
            switch_summary_df=filtered_switch_summary_df if not filtered_switch_summary_df.empty else switch_summary_df,
            top_positive_df=top_positive_df,
            top_negative_df=top_negative_df,
            outlier_report_df=outlier_report_df,
            exclusion_report_df=exclusion_report_df,
            data_quality_df=data_quality_df,
            statistical_summary_df=statistical_summary_df,
        )
        st.download_button(
            "הורדת התוצאות המסוננות לאקסל",
            data=filtered_excel,
            file_name="filtered_event_study_results.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        st.download_button(
            "הורדת קובץ אקסל מלא של הדאשבורד",
            data=full_excel,
            file_name="auditor_switch_dashboard_export.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )


def dashboard_summary_kpis_df_from_json(kpis_json: dict[str, Any], fallback_df: pd.DataFrame) -> pd.DataFrame:
    if kpis_json:
        return pd.DataFrame([kpis_json])
    return fallback_df


if __name__ == "__main__":
    main()
