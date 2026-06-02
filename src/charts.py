from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


ARROW_WHITE = "#FFFFFF"
ARROW_CYAN = "#00A6C8"
ARROW_NAVY = "#00354A"
ARROW_TEAL = "#006B7C"
ARROW_LIGHT_BG = "#F7FAFC"
ARROW_LIGHT_GRAY = "#E5E7EB"
ARROW_TEXT_GRAY = "#6B7280"
POSITIVE_GREEN = "#1E8449"
NEGATIVE_RED = "#C0392B"

ARROW_COLORWAY = [
    ARROW_CYAN,
    ARROW_TEAL,
    ARROW_NAVY,
    "#4DBFD5",
    "#7A8793",
    "#9ADBE8",
]


def _apply_arrow_layout(fig: go.Figure, height: int = 420) -> go.Figure:
    fig.update_layout(
        height=height,
        margin=dict(l=10, r=10, t=30, b=10),
        paper_bgcolor=ARROW_WHITE,
        plot_bgcolor=ARROW_WHITE,
        font=dict(color=ARROW_NAVY, family="Arial, sans-serif"),
        colorway=ARROW_COLORWAY,
        legend=dict(orientation="h", font=dict(color=ARROW_NAVY)),
        xaxis=dict(
            gridcolor=ARROW_LIGHT_GRAY,
            zerolinecolor=ARROW_LIGHT_GRAY,
            linecolor=ARROW_LIGHT_GRAY,
            tickfont=dict(color=ARROW_NAVY),
            title_font=dict(color=ARROW_NAVY),
        ),
        yaxis=dict(
            gridcolor=ARROW_LIGHT_GRAY,
            zerolinecolor=ARROW_LIGHT_GRAY,
            linecolor=ARROW_LIGHT_GRAY,
            tickfont=dict(color=ARROW_NAVY),
            title_font=dict(color=ARROW_NAVY),
        ),
    )
    return fig


def platform_bar(df: pd.DataFrame):
    data = df.groupby("Platform", as_index=False).agg({"2026 Actual": "sum", "2026 Budget": "sum"})
    data = data.sort_values("2026 Actual", ascending=True)

    fig = go.Figure()
    fig.add_bar(
        y=data["Platform"],
        x=data["2026 Budget"],
        name="Budget",
        orientation="h",
        marker_color=ARROW_TEAL,
        hovertemplate="Platform=%{y}<br>Budget=€%{x:,.0f}<extra></extra>",
    )
    fig.add_bar(
        y=data["Platform"],
        x=data["2026 Actual"],
        name="Actual",
        orientation="h",
        marker_color=ARROW_CYAN,
        hovertemplate="Platform=%{y}<br>Actual=€%{x:,.0f}<extra></extra>",
    )
    fig.update_layout(barmode="group")
    fig.update_xaxes(tickprefix="€", tickformat="~s")
    return _apply_arrow_layout(fig)


def heatmap_status(df: pd.DataFrame):
    pivot = df.pivot_table(index="Platform", columns="KPI", values="Achievement %", aggfunc="mean")
    fig = px.imshow(
        pivot,
        aspect="auto",
        labels=dict(x="KPI", y="Platform", color="Achievement"),
        text_auto=".0%",
        color_continuous_scale=[NEGATIVE_RED, ARROW_WHITE, POSITIVE_GREEN],
        zmin=0,
        zmax=1.5,
    )
    fig.update_coloraxes(colorbar_tickformat=".0%")
    return _apply_arrow_layout(fig)


def country_kpi_scatter(df: pd.DataFrame):
    fig = px.scatter(
        df,
        x="2026 Budget",
        y="2026 Actual",
        size="Investment Platform Weighting",
        color="Country",
        color_discrete_sequence=ARROW_COLORWAY,
        hover_name="Platform",
        hover_data=["KPI", "Achievement %", "Status"],
    )

    if not df.empty:
        min_budget = df["2026 Budget"].min()
        max_budget = df["2026 Budget"].max()
        fig.add_shape(
            type="line",
            x0=min_budget,
            y0=min_budget,
            x1=max_budget,
            y1=max_budget,
            line=dict(color=ARROW_NAVY, dash="dash"),
        )

    fig.update_xaxes(tickprefix="€", tickformat="~s")
    fig.update_yaxes(tickprefix="€", tickformat="~s")
    return _apply_arrow_layout(fig)


def revenue_margin_chart(df: pd.DataFrame):
    candidates = [c for c in df.columns if "EBITDA Margin" in c]
    margin_col = candidates[0] if candidates else None

    if margin_col is None:
        return _apply_arrow_layout(go.Figure())

    data = df.dropna(subset=[margin_col]).sort_values(margin_col)
    fig = px.bar(
        data,
        x=margin_col,
        y="Platform",
        orientation="h",
        hover_data=["Country", "Period"],
        color_discrete_sequence=[ARROW_CYAN],
    )
    fig.update_traces(marker_color=ARROW_CYAN)
    fig.update_xaxes(tickformat=".1%")
    return _apply_arrow_layout(fig)
