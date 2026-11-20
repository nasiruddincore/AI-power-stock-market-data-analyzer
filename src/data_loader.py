"""
Stock Market Data Loader.
Fetches historical OHLCV data via yfinance with a reliable local CSV fallback.
"""

from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd
import yfinance as yf


def generate_fallback_csv(csv_path: Path, ticker: str = "AAPL", days: int = 260) -> Path:
    """Create a deterministic realistic sample CSV when offline or if yfinance returns empty data."""
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    dates = pd.bdate_range(end=pd.Timestamp.today().normalize(), periods=days)
    rng = np.random.default_rng(42)

    daily_ret = rng.normal(loc=0.0006, scale=0.015, size=len(dates))
    close = 175.0 * np.cumprod(1.0 + daily_ret)
    open_px = close * (1.0 + rng.normal(0.0, 0.004, size=len(dates)))
    high_px = np.maximum(open_px, close) * (1.0 + np.abs(rng.normal(0.006, 0.004, size=len(dates))))
    low_px = np.minimum(open_px, close) * (1.0 - np.abs(rng.normal(0.006, 0.004, size=len(dates))))
    volume = rng.integers(25_000_000, 95_000_000, size=len(dates))

    df = pd.DataFrame(
        {
            "Date": dates.strftime("%Y-%m-%d"),
            "Open": np.round(open_px, 2),
            "High": np.round(high_px, 2),
            "Low": np.round(low_px, 2),
            "Close": np.round(close, 2),
            "Adj Close": np.round(close, 2),
            "Volume": volume,
        }
    )
    df.to_csv(csv_path, index=False)
    print(f"[INFO] Generated fallback CSV for {ticker} at {csv_path}")
    return csv_path


def _normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Flatten MultiIndex columns if present and standardize column names."""
    if df is None or df.empty:
        return pd.DataFrame()

    out = df.copy()
    if isinstance(out.columns, pd.MultiIndex):
        out.columns = [col[0] for col in out.columns]

    out = out.reset_index()
    rename_map = {
        "date": "Date",
        "open": "Open",
        "high": "High",
        "low": "Low",
        "close": "Close",
        "adj close": "Adj Close",
        "adj_close": "Adj Close",
        "volume": "Volume",
    }
    cleaned_cols = {}
    for c in out.columns:
        key = str(c).strip().lower()
        cleaned_cols[c] = rename_map.get(key, str(c).strip())
    out = out.rename(columns=cleaned_cols)

    if "Adj Close" not in out.columns and "Close" in out.columns:
        out["Adj Close"] = out["Close"]

    return out


def fetch_stock_data(
    ticker: str = "AAPL",
    start_date: str | None = None,
    end_date: str | None = None,
    period: str = "1y",
    fallback_csv: str | Path = "data/sample_stock_data.csv",
) -> tuple[pd.DataFrame, str]:
    """
    Fetch stock data from yfinance; fall back to local CSV if unavailable.
    Returns (DataFrame, source_label).
    """
    symbol = ticker.strip().upper()
    fallback_path = Path(fallback_csv)

    try:
        if start_date or end_date:
            raw = yf.download(
                symbol,
                start=start_date,
                end=end_date,
                auto_adjust=False,
                progress=False,
            )
        else:
            raw = yf.download(
                symbol,
                period=period,
                auto_adjust=False,
                progress=False,
            )

        norm = _normalize_columns(raw)
        if not norm.empty and "Date" in norm.columns and "Close" in norm.columns:
            return norm, "yfinance"
    except Exception as exc:
        print(f"[WARN] yfinance fetch failed for {symbol} ({exc}). Falling back to CSV.")

    if not fallback_path.exists():
        generate_fallback_csv(fallback_path, ticker=symbol)

    csv_df = pd.read_csv(fallback_path)
    norm_csv = _normalize_columns(csv_df)

    if "Date" in norm_csv.columns:
        dates = pd.to_datetime(norm_csv["Date"], errors="coerce")
        if start_date:
            norm_csv = norm_csv[dates >= pd.to_datetime(start_date)]
            dates = pd.to_datetime(norm_csv["Date"], errors="coerce")
        if end_date:
            norm_csv = norm_csv[dates <= pd.to_datetime(end_date)]

    return norm_csv.reset_index(drop=True), f"csv:{fallback_path}"