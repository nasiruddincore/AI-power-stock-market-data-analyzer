"""
Data Cleaning Module for Stock Market Data.
Parses dates, coerces numeric columns, removes invalid/duplicate rows, and sorts chronologically.
"""

from __future__ import annotations

import pandas as pd


REQUIRED_PRICE_COLS = ["Open", "High", "Low", "Close"]


def clean_stock_data(df: pd.DataFrame) -> pd.DataFrame:
    """Clean raw OHLCV stock data and return a sorted DataFrame indexed by Date."""
    if df is None or df.empty:
        raise ValueError("Input stock DataFrame is empty. Cannot clean data.")

    cleaned = df.copy()

    if "Date" not in cleaned.columns:
        raise ValueError("Missing 'Date' column in stock data.")

    cleaned["Date"] = pd.to_datetime(cleaned["Date"], errors="coerce")
    cleaned = cleaned.dropna(subset=["Date"])
    cleaned["Date"] = cleaned["Date"].dt.tz_localize(None)

    numeric_cols = [col for col in ["Open", "High", "Low", "Close", "Adj Close", "Volume"] if col in cleaned.columns]
    for col in numeric_cols:
        cleaned[col] = pd.to_numeric(cleaned[col], errors="coerce")

    available_prices = [col for col in REQUIRED_PRICE_COLS if col in cleaned.columns]
    if "Close" not in available_prices:
        raise ValueError("Missing 'Close' column required for stock analysis.")

    cleaned = cleaned.dropna(subset=available_prices)
    cleaned = cleaned[cleaned["Close"] > 0]

    if "Volume" in cleaned.columns:
        cleaned["Volume"] = cleaned["Volume"].fillna(0).clip(lower=0)

    cleaned = cleaned.drop_duplicates(subset=["Date"], keep="last")
    cleaned = cleaned.sort_values("Date").reset_index(drop=True)
    cleaned = cleaned.set_index("Date")

    if cleaned.empty:
        raise ValueError("No valid stock rows remained after data cleaning.")

    return cleaned