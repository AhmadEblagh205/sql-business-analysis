"""Run every analytical SQL query against the Chinook SQLite database.

Each query result is written to reports/<nn_name>.csv.  Selected analyses also
produce figures.  The SQL files remain independently readable/reusable; Python
is only orchestration and visualisation.

Usage:
    python src/download_data.py
    python src/run_analysis.py
"""
from pathlib import Path
import sqlite3

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "data" / "raw" / "chinook.sqlite"
SQL_DIR = ROOT / "sql"
REPORTS = ROOT / "reports"
FIGURES = REPORTS / "figures"


def run_all() -> None:
    if not DB.exists():
        raise SystemExit("Database not found - run src/download_data.py first.")
    REPORTS.mkdir(exist_ok=True)
    FIGURES.mkdir(parents=True, exist_ok=True)

    con = sqlite3.connect(DB)
    try:
        for sql_file in sorted(SQL_DIR.glob("*.sql")):
            query = sql_file.read_text(encoding="utf-8")
            df = pd.read_sql_query(query, con)
            out = REPORTS / f"{sql_file.stem}.csv"
            df.to_csv(out, index=False)
            print(f"\n=== {sql_file.stem} -> {out.name} ===")
            print(df.head(10).to_string(index=False))

            if sql_file.stem.startswith("05"):
                plot_monthly_trend(df)
            elif sql_file.stem.startswith("07"):
                plot_cohort_heatmap(df)
            elif sql_file.stem.startswith("08"):
                plot_pooled_activity(df)
    finally:
        con.close()


def plot_monthly_trend(df: pd.DataFrame) -> None:
    fig, ax = plt.subplots(figsize=(9, 4.5))
    ax.plot(pd.to_datetime(df["month"]), df["revenue"], lw=1.8)
    ax.set_title("Chinook store - monthly revenue")
    ax.set_xlabel("Month")
    ax.set_ylabel("Revenue (USD)")
    ax.grid(alpha=0.3)
    fig.tight_layout()
    out = FIGURES / "monthly_revenue.png"
    fig.savefig(out, dpi=150)
    plt.close(fig)
    print(f"Saved figure -> {out}")


def plot_cohort_heatmap(df: pd.DataFrame, max_months: int = 24) -> None:
    """Plot exact-month repeat-purchase activity with zeros represented honestly."""
    shown = df[df["month_offset"] <= max_months].copy()
    matrix = shown.pivot(index="cohort", columns="month_offset", values="activity_pct")

    fig, ax = plt.subplots(figsize=(11, 6.2))
    image = ax.imshow(matrix.to_numpy(dtype=float), aspect="auto", interpolation="nearest")
    ax.set_title("Cohort repeat-purchase activity by exact month")
    ax.set_xlabel("Months since first purchase")
    ax.set_ylabel("First-purchase cohort")
    ax.set_xticks(np.arange(len(matrix.columns)))
    ax.set_xticklabels(matrix.columns.astype(int), fontsize=8)
    step = max(1, len(matrix.index) // 10)
    yticks = np.arange(0, len(matrix.index), step)
    ax.set_yticks(yticks)
    ax.set_yticklabels(matrix.index[yticks], fontsize=8)
    cbar = fig.colorbar(image, ax=ax)
    cbar.set_label("Active customers in that month (%)")
    fig.tight_layout()
    out = FIGURES / "cohort_activity_heatmap.png"
    fig.savefig(out, dpi=150)
    plt.close(fig)
    print(f"Saved figure -> {out}")


def plot_pooled_activity(df: pd.DataFrame, max_months: int = 24) -> None:
    shown = df[df["month_offset"] <= max_months]
    fig, ax = plt.subplots(figsize=(9, 4.5))
    ax.plot(shown["month_offset"], shown["pooled_activity_pct"], marker="o", ms=3)
    ax.set_title("Pooled cohort repeat-purchase activity")
    ax.set_xlabel("Months since first purchase")
    ax.set_ylabel("Eligible customers active that month (%)")
    ax.set_ylim(bottom=0)
    ax.grid(alpha=0.3)
    fig.tight_layout()
    out = FIGURES / "cohort_activity_pooled.png"
    fig.savefig(out, dpi=150)
    plt.close(fig)
    print(f"Saved figure -> {out}")


if __name__ == "__main__":
    run_all()
