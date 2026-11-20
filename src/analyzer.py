"""
Stock Market Analytics Engine.
Computes daily returns, moving averages, trend regime, price extremes, volatility, and optional TA/backtest.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

try:
    from ta.momentum import RSIIndicator
    from ta.trend import MACD, SMAIndicator
    from ta.volatility import BollingerBands
    HAS_TA = True
except ImportError:
    HAS_TA = False


TRADING_DAYS_PER_YEAR = 252


def analyze_stock(
    df: pd.DataFrame,
    short_window: int = 20,
    long_window: int = 50,
    risk_free_rate: float = 0.04,
) -> tuple[pd.DataFrame, dict]:
    """
    Compute moving averages, daily returns, volatility, price highs/lows, and summary metrics.
    Returns (enriched_df, summary_dict).
    """
    if df is None or df.empty or "Close" not in df.columns:
        raise ValueError("Cleaned DataFrame with 'Close' column is required.")

    data = df.copy()

    # Daily percentage returns and log returns
    data["Daily_Return"] = data["Close"].pct_change()
    data["Daily_Return_Pct"] = data["Daily_Return"] * 100.0
    data["Log_Return"] = np.log(data["Close"] / data["Close"].shift(1))

    # Moving averages
    data[f"SMA_{short_window}"] = data["Close"].rolling(window=short_window, min_periods=1).mean()
    data[f"SMA_{long_window}"] = data["Close"].rolling(window=long_window, min_periods=1).mean()

    # Rolling annualized volatility (20-day window)
    data["Rolling_Volatility_Pct"] = (
        data["Daily_Return"].rolling(window=20, min_periods=5).std() * np.sqrt(TRADING_DAYS_PER_YEAR) * 100.0
    )

    # Trend classification based on short vs long moving average and price vs long MA
    short_col = f"SMA_{short_window}"
    long_col = f"SMA_{long_window}"
    conditions = [
        (data[short_col] > data[long_col]) & (data["Close"] >= data[long_col]),
        (data[short_col] < data[long_col]) & (data["Close"] <= data[long_col]),
    ]
    choices = ["Uptrend (Bullish)", "Downtrend (Bearish)"]
    data["Trend"] = np.select(conditions, choices, default="Sideways / Consolidation")

    # Optional technical indicators via `ta`
    if HAS_TA and len(data) >= 26:
        close_s = data["Close"]
        data["SMA_20_TA"] = SMAIndicator(close_s, window=20).sma_indicator()
        data["SMA_50_TA"] = SMAIndicator(close_s, window=50).sma_indicator()
        data["RSI_14"] = RSIIndicator(close_s, window=14).rsi()
        macd_obj = MACD(close_s)
        data["MACD"] = macd_obj.macd()
        data["MACD_Signal"] = macd_obj.macd_signal()
        data["MACD_Hist"] = macd_obj.macd_diff()
        bb_obj = BollingerBands(close_s, window=20, window_dev=2)
        data["BB_Upper"] = bb_obj.bollinger_hband()
        data["BB_Mid"] = bb_obj.bollinger_mavg()
        data["BB_Lower"] = bb_obj.bollinger_lband()

    valid_returns = data["Daily_Return"].dropna()
    start_price = float(data["Close"].iloc[0])
    end_price = float(data["Close"].iloc[-1])
    total_return_pct = ((end_price - start_price) / start_price) * 100.0

    high_idx = data["High"].idxmax() if "High" in data.columns else data["Close"].idxmax()
    low_idx = data["Low"].idxmin() if "Low" in data.columns else data["Close"].idxmin()
    highest_price = float(data.loc[high_idx, "High"]) if "High" in data.columns else float(data.loc[high_idx, "Close"])
    lowest_price = float(data.loc[low_idx, "Low"]) if "Low" in data.columns else float(data.loc[low_idx, "Close"])

    avg_daily_return_pct = float(valid_returns.mean() * 100.0) if not valid_returns.empty else 0.0
    daily_std = float(valid_returns.std()) if not valid_returns.empty else 0.0
    annualized_volatility_pct = float(daily_std * np.sqrt(TRADING_DAYS_PER_YEAR) * 100.0)

    best_day_date = valid_returns.idxmax() if not valid_returns.empty else data.index[-1]
    worst_day_date = valid_returns.idxmin() if not valid_returns.empty else data.index[-1]
    best_day_pct = float(valid_returns.max() * 100.0) if not valid_returns.empty else 0.0
    worst_day_pct = float(valid_returns.min() * 100.0) if not valid_returns.empty else 0.0

    # Cumulative return & Maximum Drawdown
    cum_wealth = (1.0 + data["Daily_Return"].fillna(0.0)).cumprod()
    running_peak = cum_wealth.cummax()
    drawdown = (cum_wealth / running_peak) - 1.0
    max_drawdown_pct = float(drawdown.min() * 100.0)

    # Annualized Sharpe Ratio (simple approximation)
    ann_return = float(valid_returns.mean() * TRADING_DAYS_PER_YEAR) if not valid_returns.empty else 0.0
    ann_vol = float(daily_std * np.sqrt(TRADING_DAYS_PER_YEAR))
    sharpe_ratio = float((ann_return - risk_free_rate) / ann_vol) if ann_vol > 1e-9 else 0.0

    latest_trend = str(data["Trend"].iloc[-1])

    summary = {
        "start_date": data.index[0].strftime("%Y-%m-%d"),
        "end_date": data.index[-1].strftime("%Y-%m-%d"),
        "trading_days": int(len(data)),
        "start_price": round(start_price, 2),
        "end_price": round(end_price, 2),
        "total_return_pct": round(total_return_pct, 2),
        "highest_price": round(highest_price, 2),
        "highest_price_date": pd.Timestamp(high_idx).strftime("%Y-%m-%d"),
        "lowest_price": round(lowest_price, 2),
        "lowest_price_date": pd.Timestamp(low_idx).strftime("%Y-%m-%d"),
        "avg_daily_return_pct": round(avg_daily_return_pct, 4),
        "annualized_volatility_pct": round(annualized_volatility_pct, 2),
        "max_drawdown_pct": round(max_drawdown_pct, 2),
        "sharpe_ratio": round(sharpe_ratio, 2),
        "best_day_pct": round(best_day_pct, 2),
        "best_day_date": pd.Timestamp(best_day_date).strftime("%Y-%m-%d"),
        "worst_day_pct": round(worst_day_pct, 2),
        "worst_day_date": pd.Timestamp(worst_day_date).strftime("%Y-%m-%d"),
        "latest_trend": latest_trend,
        "latest_short_ma": round(float(data[short_col].iloc[-1]), 2),
        "latest_long_ma": round(float(data[long_col].iloc[-1]), 2),
    }

    return data, summary


def run_sma_crossover_backtest(
    df: pd.DataFrame,
    short_col: str = "SMA_20",
    long_col: str = "SMA_50",
    fee_bps: float = 5.0,
) -> dict:
    """
    Lagged long-only moving average crossover backtest with transaction cost in basis points (1 bps = 0.01%).
    Uses pos = signal.shift(1) to avoid same-bar look-ahead bias.
    """
    bt_df = df.copy().dropna(subset=["Close", short_col, long_col])
    if len(bt_df) < 2:
        return {
            "total_return_pct": 0.0,
            "max_drawdown_pct": 0.0,
            "sharpe_ratio": 0.0,
            "trades": 0,
            "win_rate_pct": 0.0,
        }

    signal = (bt_df[short_col] > bt_df[long_col]).astype(int)
    position = signal.shift(1).fillna(0)
    asset_ret = bt_df["Close"].pct_change().fillna(0.0)
    gross_ret = position * asset_ret

    turnover = (position.diff().abs().fillna(0) > 0).astype(int)
    fee_rate = fee_bps / 10_000.0
    net_ret = gross_ret - (turnover * fee_rate)

    equity = (1.0 + net_ret).cumprod()
    total_ret_pct = float((equity.iloc[-1] - 1.0) * 100.0)
    max_dd_pct = float(((equity / equity.cummax()) - 1.0).min() * 100.0)

    step_ret = equity.pct_change().fillna(0.0)
    vol = float(step_ret.std())
    sharpe = float((step_ret.mean() * np.sqrt(TRADING_DAYS_PER_YEAR)) / vol) if vol > 1e-9 else 0.0

    trades = int(turnover.sum())
    trade_returns = net_ret[turnover == 1]
    win_rate_pct = float((trade_returns > 0).mean() * 100.0) if trades > 0 else 0.0

    return {
        "total_return_pct": round(total_ret_pct, 2),
        "max_drawdown_pct": round(max_dd_pct, 2),
        "sharpe_ratio": round(sharpe, 2),
        "trades": trades,
        "win_rate_pct": round(win_rate_pct, 2),
    }