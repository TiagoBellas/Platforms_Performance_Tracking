from __future__ import annotations

from pathlib import Path
import pandas as pd
import numpy as np

DATA_DIR = Path(__file__).resolve().parents[1] / "data"

FINANCIAL_SHEETS = {
    "Capital_Committ_Fund_Perform": "Capital_Committ_Fund_Perform.csv",
    "Realisations_Fund_Perform": "Realisations_Fund_Perform.csv",
    "EBITDA": "EBITDA.csv",
    "EBITDA Margin": "EBITDA_Margin.csv",
}

QUALITATIVE_SHEETS = {
    "Business Performance & ESG": "Business_Performance_ESG.csv",
    "Platform Performance": "Platform_Performance.csv",
    "Business Performance & ESG_V1": "Business_Performance_ESG_V1.csv",
    "Platform Performance_V1": "Platform_Performance_V1.csv",
}


def _safe_numeric(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series, errors="coerce")


def load_financial_kpis() -> pd.DataFrame:
    frames: list[pd.DataFrame] = []
    for source_sheet, filename in FINANCIAL_SHEETS.items():
        path = DATA_DIR / filename
        df = pd.read_csv(path)
        df = df.dropna(how="all")
        df["Source Sheet"] = source_sheet
        for col in [
            "LQ_Floor",
            "Investment Platform Weighting",
            "Servicing Platform Weighting",
            "2026 Budget",
            "2026 Actual",
            "Total Fund",
            "Total Arrow Backbook",
        ]:
            if col in df.columns:
                df[col] = _safe_numeric(df[col])
        frames.append(df)
    base = pd.concat(frames, ignore_index=True, sort=False)
    base["Period"] = base["Period"].fillna("Unknown")
    base["Variance"] = base["2026 Actual"] - base["2026 Budget"]
    base["Variance %"] = np.where(base["2026 Budget"].abs() > 0, base["Variance"] / base["2026 Budget"].abs(), np.nan)
    base["Achievement %"] = np.where(base["2026 Budget"].abs() > 0, base["2026 Actual"] / base["2026 Budget"], np.nan)
    base["Weighted Score Investment"] = base["Achievement %"] * base["Investment Platform Weighting"].fillna(0)
    base["Weighted Score Servicing"] = base["Achievement %"] * base["Servicing Platform Weighting"].fillna(0)
    base["Status"] = np.select(
        [
            base["Achievement %"].isna(),
            base["Achievement %"] < base["LQ_Floor"].fillna(0.90),
            base["Achievement %"].between(0.95, 1.05, inclusive="both"),
            base["Achievement %"] > 1.05,
        ],
        ["No data", "Below floor", "On target", "Above target"],
        default="Watch",
    )
    return base


def load_revenue() -> pd.DataFrame:
    df = pd.read_csv(DATA_DIR / "Revenue.csv")
    df = df.dropna(how="all")
    # The Excel file contains duplicate column names; pandas suffixes repeated names with .1
    numeric_cols = [c for c in df.columns if c not in {"Platform", "Country", "Period"}]
    for col in numeric_cols:
        df[col] = _safe_numeric(df[col])
    return df


def load_qualitative() -> pd.DataFrame:
    frames: list[pd.DataFrame] = []
    for source_sheet, filename in QUALITATIVE_SHEETS.items():
        df = pd.read_csv(DATA_DIR / filename)
        df = df.dropna(how="all")
        df["Source Sheet"] = source_sheet
        df["Category"] = np.where(df["Source Sheet"].str.contains("ESG", case=False), "Business Performance & ESG", "Platform Performance")
        for col in ["Investment Platform Weighting", "Servicing Platform Weighting"]:
            df[col] = _safe_numeric(df[col])
        frames.append(df)
    return pd.concat(frames, ignore_index=True, sort=False)


def load_extraction_summary() -> pd.DataFrame:
    return pd.read_csv(DATA_DIR / "Extraction_Summary.csv", header=None)
