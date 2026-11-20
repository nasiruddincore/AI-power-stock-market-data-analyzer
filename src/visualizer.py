"""
Visualization Module for Stock Market Data Analyzer.
Generates trend, moving average, and daily return/volatility charts.
"""

from __future__ import annotations

from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


sns.set_theme(style="whitegrid")


def create_charts(
    df: pd.DataFrame,
    ticker: str,
    images_dir: str | Path = "images",
    outputs_dir: str | Path = "outputs",
    short_window: int = 20,
    long_window: int = 50,
) -> dict[str, Path]:
    """Generate and save trend, moving average, and daily return charts."""
    symbol = ticker.strip().upper()
    img_path = Path(images_dir)
    out_path = Path(outputs_dir)
    img_path.mkdir(parents=True, exist_ok=True)
    out_path.mkdir(parents=True, exist_ok=True)

    saved_paths: dict[str, Path] = {}

    # 1. Closing Price & Trend Chart
    fig, ax = plt.subplots(figsize=(11, 5))
    ax.plot(df.index, df["Close"], label="Close Price", color="#1f77b4", linewidth=2)
    if "High" in df.columns and "Low" in df.columns:
        ax.fill_between(
            df.index,
            df["Low"],
            df["High"],
            color="#1f77b4",
            alpha=0.10,
            label="Daily High-Low Range",
        )
    ax.set_title(f"{symbol} — Closing Price & Price Range Trend", fontsize=13, fontweight="bold")
    ax.set_xlabel("Date")
    ax.set_ylabel("Price ($)")
    ax.legend(loc="best")
    fig.tight_layout()

    trend_file = img_path / f"{symbol.lower()}_trend.png"
    fig.savefig(trend_file, dpi=150)
    fig.savefig(out_path / f"{symbol.lower()}_trend.png", dpi=150)
    plt.close(fig)
    saved_paths["trend_chart"] = trend_file

    # 2. Moving Average Chart
    short_col = f"SMA_{short_window}"
    long_col = f"SMA_{long_window}"
    fig, ax = plt.subplots(figsize=(11, 5))
    ax.plot(df.index, df["Close"], label="Close Price", color="#222222", linewidth=1.8, alpha=0.85)
    if short_col in df.columns:
        ax.plot(df.index, df[short_col], label=f"{short_window}-Day SMA", color="#008080", linewidth=1.6)
    if long_col in df.columns:
        ax.plot(df.index, df[long_col], label=f"{long_window}-Day SMA", color="#d95f02", linewidth=1.6)
    ax.set_title(f"{symbol} — Moving Averages ({short_window}d vs {long_window}d)", fontsize=13, fontweight="bold")
    ax.set_xlabel("Date")
    ax.set_ylabel("Price ($)")
    ax.legend(loc="best")
    fig.tight_layout()

    ma_file = img_path / f"{symbol.lower()}_moving_averages.png"
    fig.savefig(ma_file, dpi=150)
    fig.savefig(out_path / f"{symbol.lower()}_moving_averages.png", dpi=150)
    plt.close(fig)
    saved_paths["ma_chart"] = ma_file

    # 3. Daily Returns & Distribution Chart
    returns_pct = df["Daily_Return_Pct"].dropna()
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4.8))

    colors = ["#2ca02c" if val >= 0 else "#d62728" for val in returns_pct]
    ax1.bar(returns_pct.index, returns_pct.values, color=colors, width=1.2, alpha=0.8)
    ax1.axhline(0, color="black", linewidth=0.9)
    ax1.set_title(f"{symbol} — Daily Returns (%)", fontsize=12, fontweight="bold")
    ax1.set_xlabel("Date")
    ax1.set_ylabel("Daily Return (%)")

    sns.histplot(returns_pct, kde=True, bins=30, color="#4c72b0", ax=ax2)
    ax2.axvline(0, color="black", linestyle="--", linewidth=1)
    ax2.set_title(f"{symbol} — Return Distribution & Volatility", fontsize=12, fontweight="bold")
    ax2.set_xlabel("Daily Return (%)")
    ax2.set_ylabel("Frequency")

    fig.tight_layout()
    ret_file = img_path / f"{symbol.lower()}_daily_returns.png"
    fig.savefig(ret_file, dpi=150)
    fig.savefig(out_path / f"{symbol.lower()}_daily_returns.png", dpi=150)
    plt.close(fig)
    saved_paths["returns_chart"] = ret_file

    return saved_paths