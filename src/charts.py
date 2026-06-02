from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def platform_bar(df: pd.DataFrame):
    data = df.groupby("Platform", as_index=False).agg({"2026 Actual": "sum", "2026 Budget": "sum"})
    data = data.sort_values("2026 Actual", ascending=True)
    fig = go.Figure()
    fig.add_bar(y=data["Platform"], x=data["2026 Budget"], name="Budget", orientation="h")
    fig.add_bar(y=data["Platform"], x=data["2026 Actual"], name="Actual", orientation="h")
    fig.update_layout(barmode="group", height=420, margin=dict(l=10, r=10, t=30, b=10), legend=dict(orientation="h"))
    return fig


def heatmap_status(df: pd.DataFrame):
    pivot = df.pivot_table(index="Platform", columns="KPI", values="Achievement %", aggfunc="mean")
    fig = px.imshow(
        pivot,
        aspect="auto",
        labels=dict(x="KPI", y="Platform", color="Achievement"),
        text_auto=".0%",
    )
    fig.update_layout(height=420, margin=dict(l=10, r=10, t=30, b=10))
    return fig


def country_kpi_scatter(df: pd.DataFrame):
    fig = px.scatter(
        df,
        x="2026 Budget",
        y="2026 Actual",
        size="Investment Platform Weighting",
        color="Country",
        hover_name="Platform",
        hover_data=["KPI", "Achievement %", "Status"],
    )
    fig.add_shape(type="line", x0=df["2026 Budget"].min(), y0=df["2026 Budget"].min(), x1=df["2026 Budget"].max(), y1=df["2026 Budget"].max(), line=dict(dash="dash"))
    fig.update_layout(height=420, margin=dict(l=10, r=10, t=30, b=10))
    return fig


def revenue_margin_chart(df: pd.DataFrame):
    candidates = [c for c in df.columns if "EBITDA Margin" in c]
    margin_col = candidates[0] if candidates else None
    if margin_col is None:
        return go.Figure()
    data = df.dropna(subset=[margin_col]).sort_values(margin_col)
    fig = px.bar(data, x=margin_col, y="Platform", orientation="h", hover_data=["Country", "Period"])
    fig.update_layout(height=420, margin=dict(l=10, r=10, t=30, b=10), xaxis_tickformat=".1%")
    return fig
