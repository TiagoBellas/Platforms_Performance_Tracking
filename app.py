from __future__ import annotations

import streamlit as st
import pandas as pd

from src.data_loader import load_financial_kpis, load_revenue, load_qualitative, load_extraction_summary
from src.charts import platform_bar, heatmap_status, country_kpi_scatter, revenue_margin_chart


# =========================
# Page setup
# =========================
st.set_page_config(page_title="Performance Tracking Dashboard", page_icon="📊", layout="wide")


# =========================
# Arrow Global color palette
# =========================
ARROW_WHITE = "#FFFFFF"
ARROW_CYAN = "#00A6C8"
ARROW_NAVY = "#00354A"
ARROW_TEAL = "#006B7C"
ARROW_LIGHT_BG = "#F7FAFC"
ARROW_LIGHT_CYAN = "#E6F7FB"
ARROW_LIGHT_GRAY = "#E5E7EB"
ARROW_TEXT_GRAY = "#6B7280"
POSITIVE_GREEN = "#1E8449"
NEGATIVE_RED = "#C0392B"


st.markdown(
    f"""
    <style>
    /* =========================
       Arrow Global theme
       ========================= */

    .stApp {{
        background-color: {ARROW_WHITE};
    }}

    .block-container {{
        padding-top: 2rem;
        padding-bottom: 2rem;
    }}

    body, .stMarkdown, .stText, p, span, div {{
        color: {ARROW_NAVY};
    }}

    h1 {{
        color: {ARROW_NAVY};
        font-weight: 700;
    }}

    h2, h3 {{
        color: {ARROW_TEAL};
        font-weight: 600;
    }}

    .stCaptionContainer {{
        color: {ARROW_TEXT_GRAY};
    }}

    section[data-testid="stSidebar"] {{
        background-color: {ARROW_LIGHT_BG};
        border-right: 1px solid {ARROW_LIGHT_GRAY};
    }}

    section[data-testid="stSidebar"] * {{
        color: {ARROW_NAVY};
    }}

    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3 {{
        color: {ARROW_NAVY};
    }}

    label {{
        color: {ARROW_NAVY} !important;
        font-weight: 600;
    }}

    div[data-baseweb="select"] > div {{
        background-color: {ARROW_WHITE};
        border-color: {ARROW_LIGHT_GRAY};
        color: {ARROW_NAVY};
    }}

    div[data-baseweb="select"] span {{
        color: {ARROW_NAVY};
    }}

    span[data-baseweb="tag"] {{
        background-color: {ARROW_LIGHT_CYAN} !important;
        color: {ARROW_NAVY} !important;
    }}

    button[data-baseweb="tab"] {{
        background-color: {ARROW_WHITE};
        color: {ARROW_NAVY};
        border-radius: 8px 8px 0 0;
        padding: 8px 16px;
        border-bottom: 2px solid transparent;
        font-weight: 600;
    }}

    button[data-baseweb="tab"][aria-selected="true"] {{
        background-color: {ARROW_WHITE};
        color: {ARROW_CYAN};
        border-bottom: 3px solid {ARROW_CYAN};
        font-weight: 700;
    }}

    .stButton > button,
    .stDownloadButton > button {{
        background-color: {ARROW_CYAN};
        color: {ARROW_WHITE};
        border-radius: 8px;
        border: none;
        font-weight: 600;
    }}

    .stButton > button:hover,
    .stDownloadButton > button:hover {{
        background-color: {ARROW_TEAL};
        color: {ARROW_WHITE};
        border: none;
    }}

    div[data-testid="stDataFrame"] {{
        border: 1px solid {ARROW_LIGHT_GRAY};
        border-radius: 10px;
    }}

    details {{
        background-color: {ARROW_WHITE};
        border: 1px solid {ARROW_LIGHT_GRAY};
        border-radius: 10px;
    }}

    details summary {{
        color: {ARROW_NAVY};
        font-weight: 600;
    }}

    div[role="radiogroup"] label {{
        color: {ARROW_NAVY} !important;
    }}

    div[data-testid="stMetric"] {{
        background-color: {ARROW_WHITE};
        border: 1px solid {ARROW_LIGHT_GRAY};
        border-top: 5px solid {ARROW_CYAN};
        border-radius: 14px;
        padding: 18px 20px;
        box-shadow: 0 1px 4px rgba(0, 53, 74, 0.08);
    }}

    div[data-testid="stMetricLabel"] {{
        color: {ARROW_TEXT_GRAY};
        font-weight: 600;
    }}

    div[data-testid="stMetricValue"] {{
        color: {ARROW_NAVY};
        font-weight: 800;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data(show_spinner=False)
def get_data():
    return load_financial_kpis(), load_revenue(), load_qualitative(), load_extraction_summary()


financial, revenue, qualitative, extraction = get_data()


st.title("Performance Tracking Dashboard")
st.caption("Acompanhamento de performance por Platform, país, KPI e período — baseado no ficheiro log_scorecardPerformanceTracking.xlsx")


with st.sidebar:
    st.header("Filtros")

    periods = sorted(financial["Period"].dropna().unique().tolist())
    selected_periods = st.multiselect("Período", periods, default=periods)

    platforms = sorted(financial["Platform"].dropna().unique().tolist())
    selected_platforms = st.multiselect("Platform", platforms, default=platforms)

    countries = sorted(financial["Country"].dropna().unique().tolist())
    selected_countries = st.multiselect("País", countries, default=countries)

    kpis = sorted(financial["KPI"].dropna().unique().tolist())
    selected_kpis = st.multiselect("KPI", kpis, default=kpis)


mask = (
    financial["Period"].isin(selected_periods)
    & financial["Platform"].isin(selected_platforms)
    & financial["Country"].isin(selected_countries)
    & financial["KPI"].isin(selected_kpis)
)

f = financial.loc[mask].copy()


actual = f["2026 Actual"].sum()
budget = f["2026 Budget"].sum()
variance = actual - budget
achievement = actual / budget if budget else None
on_target = (f["Status"] == "On target").mean() if len(f) else 0


def format_currency_dynamic(value: float | int | None) -> str:
    """Format currency values dynamically as K, m, or Bn."""
    if value is None or pd.isna(value):
        return "N/A"

    abs_value = abs(value)

    if abs_value >= 1_000_000_000:
        return f"€{value / 1_000_000_000:.1f}Bn"
    if abs_value >= 1_000_000:
        return f"€{value / 1_000_000:.1f}m"
    if abs_value >= 1_000:
        return f"€{value / 1_000:.1f}K"

    return f"€{value:,.0f}"


def metric_color(value: float | int | None) -> str:
    if value is None or pd.isna(value):
        return ARROW_TEXT_GRAY
    if value < 0:
        return NEGATIVE_RED
    if value > 0:
        return POSITIVE_GREEN
    return ARROW_TEXT_GRAY


def colored_metric(container, label: str, value: float | int | None) -> None:
    color = metric_color(value)
    formatted_value = format_currency_dynamic(value)

    container.markdown(
        f"""
        <div style="
            background-color:{ARROW_WHITE};
            padding:18px 20px;
            border-radius:14px;
            border:1px solid {ARROW_LIGHT_GRAY};
            border-top:5px solid {ARROW_CYAN};
            box-shadow:0 1px 4px rgba(0, 53, 74, 0.08);
        ">
            <div style="
                font-size:14px;
                color:{ARROW_TEXT_GRAY};
                margin-bottom:6px;
                font-weight:600;
            ">
                {label}
            </div>
            <div style="
                font-size:30px;
                font-weight:800;
                color:{color};
            ">
                {formatted_value}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


c1, c2, c3, c4 = st.columns(4)

colored_metric(c1, "Actual 2026", actual)
colored_metric(c2, "Budget 2026", budget)
colored_metric(c3, "Variance", variance)
c4.metric("KPIs On Target", f"{on_target:.0%}")


financial_tab, revenue_tab, qualitative_tab, data_tab = st.tabs(
    ["Finance KPIs", "Revenue / EBITDA", "Qualitativos", "Dados"]
)


with financial_tab:
    left, right = st.columns([1.1, 0.9])

    with left:
        st.subheader("Actual vs Budget por Platform")
        st.plotly_chart(platform_bar(f), use_container_width=True)

    with right:
        st.subheader("Achievement heatmap")
        st.plotly_chart(heatmap_status(f), use_container_width=True)

    st.subheader("Dispersão por país")
    st.plotly_chart(country_kpi_scatter(f), use_container_width=True)

    st.subheader("Tabela de KPIs financeiros")
    st.dataframe(
        f[
            [
                "Platform",
                "Country",
                "KPI",
                "Period",
                "2026 Budget",
                "2026 Actual",
                "Variance",
                "Achievement %",
                "Status",
                "Investment Platform Weighting",
                "Servicing Platform Weighting",
            ]
        ].sort_values(["Country", "Platform", "KPI"]),
        use_container_width=True,
        hide_index=True,
        column_config={
            "2026 Budget": st.column_config.NumberColumn(format="€%.0f"),
            "2026 Actual": st.column_config.NumberColumn(format="€%.0f"),
            "Variance": st.column_config.NumberColumn(format="€%.0f"),
            "Achievement %": st.column_config.ProgressColumn(
                format="%.0f%%",
                min_value=0,
                max_value=1.5,
            ),
        },
    )


with revenue_tab:
    st.subheader("Revenue / EBITDA")

    rv = revenue[
        revenue["Platform"].isin(selected_platforms)
        & revenue["Country"].isin(selected_countries)
        & revenue["Period"].isin(selected_periods)
    ].copy()

    st.plotly_chart(revenue_margin_chart(rv), use_container_width=True)
    st.dataframe(rv, use_container_width=True, hide_index=True)


with qualitative_tab:
    st.subheader("Objetivos qualitativos e pesos")

    q = qualitative[
        qualitative["Platform"].isin(selected_platforms)
        & qualitative["Country"].isin(selected_countries)
    ]

    category = st.radio(
        "Categoria",
        sorted(q["Category"].dropna().unique().tolist()),
        horizontal=True,
    )

    q = q[q["Category"] == category]

    for _, row in q.sort_values(["Country", "Platform"]).iterrows():
        with st.expander(
            f"{row['Platform']} | {row['Country']} | "
            f"Investment {row['Investment Platform Weighting']:.0%} / "
            f"Servicing {row['Servicing Platform Weighting']:.0%}"
        ):
            st.write(row["KPI"])


with data_tab:
    st.subheader("Rastreabilidade da extração")

    st.dataframe(extraction, use_container_width=True, hide_index=True)

    st.download_button(
        "Download dados financeiros normalizados",
        data=f.to_csv(index=False).encode("utf-8"),
        file_name="financial_kpis_filtered.csv",
        mime="text/csv",
    )
