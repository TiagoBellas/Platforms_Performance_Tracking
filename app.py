from __future__ import annotations

import streamlit as st
import pandas as pd

from src.data_loader import load_financial_kpis, load_revenue, load_qualitative, load_extraction_summary
from src.charts import platform_bar, heatmap_status, country_kpi_scatter, revenue_margin_chart


st.set_page_config(page_title="Performance Tracking Dashboard", page_icon="📊", layout="wide")


st.markdown(
    """
    <style>
    /* =========================
       Paleta Arrow Global
       =========================
       Fundo: #FFFFFF
       Azul Arrow: #00A6C8
       Azul escuro: #00354A
       Azul petróleo: #006B7C
       Cinza claro: #E5E7EB
       Cinza texto: #6B7280
    */

    /* Fundo geral */
    .stApp {
        background-color: #FFFFFF;
    }

    /* Container principal */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }

    /* Texto principal */
    body, .stMarkdown, .stText, p, span, div {
        color: #00354A;
    }

    /* Título principal */
    h1 {
        color: #00354A;
        font-weight: 700;
    }

    /* Subtítulos */
    h2, h3 {
        color: #006B7C;
        font-weight: 600;
    }

    /* Caption / texto auxiliar */
    .stCaptionContainer {
        color: #6B7280;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #F7FAFC;
        border-right: 1px solid #E5E7EB;
    }

    section[data-testid="stSidebar"] * {
        color: #00354A;
    }

    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3 {
        color: #00354A;
    }

    /* Labels dos filtros */
    label {
        color: #00354A !important;
        font-weight: 600;
    }

    /* Multiselect / inputs */
    div[data-baseweb="select"] > div {
        background-color: #FFFFFF;
        border-color: #E5E7EB;
        color: #00354A;
    }

    div[data-baseweb="select"] span {
        color: #00354A;
    }

    /* Tags selecionadas nos multiselects */
    span[data-baseweb="tag"] {
        background-color: #E6F7FB !important;
        color: #00354A !important;
    }

    /* Tabs */
    button[data-baseweb="tab"] {
        background-color: #FFFFFF;
        color: #00354A;
        border-radius: 8px 8px 0 0;
        padding: 8px 16px;
        border-bottom: 2px solid transparent;
        font-weight: 600;
    }

    /* Tab ativa */
    button[data-baseweb="tab"][aria-selected="true"] {
        background-color: #FFFFFF;
        color: #00A6C8;
        border-bottom: 3px solid #00A6C8;
        font-weight: 700;
    }

    /* Botões */
    .stButton > button,
    .stDownloadButton > button {
        background-color: #00A6C8;
        color: #FFFFFF;
        border-radius: 8px;
        border: none;
        font-weight: 600;
    }

    .stButton > button:hover,
    .stDownloadButton > button:hover {
        background-color: #006B7C;
        color: #FFFFFF;
        border: none;
    }

    /* Dataframes */
    div[data-testid="stDataFrame"] {
        border: 1px solid #E5E7EB;
        border-radius: 10px;
    }

    /* Expanders */
    details {
        background-color: #FFFFFF;
        border: 1px solid #E5E7EB;
        border-radius: 10px;
    }

    details summary {
        color: #00354A;
        font-weight: 600;
    }

    /* Radio buttons */
    div[role="radiogroup"] label {
        color: #00354A !important;
    }

    /* Métrica nativa do Streamlit */
    div[data-testid="stMetric"] {
        background-color: #FFFFFF;
        border: 1px solid #E5E7EB;
        border-top: 5px solid #00A6C8;
        border-radius: 14px;
        padding: 18px 20px;
        box-shadow: 0 1px 4px rgba(0, 53, 74, 0.08);
    }

    div[data-testid="stMetricLabel"] {
        color: #6B7280;
        font-weight: 600;
    }

    div[data-testid="stMetricValue"] {
        color: #00354A;
        font-weight: 800;
    }
    </style>
    """,
    unsafe_allow_html=True
)


st.image("data/logo.jpg", width=180)


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


def format_currency_dynamic(value):
    abs_value = abs(value)

    if abs_value >= 1_000_000_000:
        return f"€{value / 1_000_000_000:.1f}Bn"
    elif abs_value >= 1_000_000:
        return f"€{value / 1_000_000:.1f}m"
    elif abs_value >= 1_000:
        return f"€{value / 1_000:.1f}K"
    else:
        return f"€{value:,.0f}"


def metric_color(value):
    if value < 0:
        return "#C0392B"
    elif value > 0:
        return "#1E8449"
    else:
        return "#6B7280"


def colored_metric(container, label, value):
    color = metric_color(value)
    formatted_value = format_currency_dynamic(value)

    container.markdown(
        f"""
        <div style="
            background-color:#FFFFFF;
            padding:18px 20px;
            border-radius:14px;
            border:1px solid #E5E7EB;
            border-top:5px solid #00A6C8;
            box-shadow:0 1px 4px rgba(0, 53, 74, 0.08);
        ">
            <div style="
                font-size:14px;
                color:#6B7280;
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
        unsafe_allow_html=True
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
                format="%.0f%",
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
