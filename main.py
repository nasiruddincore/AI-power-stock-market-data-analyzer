"""
Main Entry Point for Stock Market Data Analyzer.
Usage:
    python main.py --ticker AAPL --period 1y
    python main.py --ticker MSFT --start 2024-01-01 --end 2026-11-01
"""

from __future__ import annotations

import argparse
from src.analyzer import analyze_stock, run_sma_crossover_backtest
from src.cleaner import clean_stock_data
from src.data_loader import fetch_stock_data
from src.report_generator import generate_report
from src.visualizer import create_charts


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run Stock Market Data Analyzer pipeline.")
    parser.add_argument("--ticker", type=str, default="AAPL", help="Stock ticker symbol (e.g., AAPL, MSFT, RELIANCE.NS)")
    parser.add_argument("--period", type=str, default="1y", help="yfinance period if start/end not set (e.g., 6mo, 1y, 2y)")
    parser.add_argument("--start", type=str, default=None, help="Start date YYYY-MM-DD")
    parser.add_argument("--end", type=str, default=None, help="End date YYYY-MM-DD")
    parser.add_argument("--short-ma", type=int, default=20, help="Short moving average window")
    parser.add_argument("--long-ma", type=int, default=50, help="Long moving average window")
    parser.add_argument("--fee-bps", type=float, default=5.0, help="Backtest transaction fee in basis points")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    symbol = args.ticker.strip().upper()

    raw_df, source_label = fetch_stock_data(
        ticker=symbol,
        start_date=args.start,
        end_date=args.end,
        period=args.period,
    )
    clean_df = clean_stock_data(raw_df)
    analyzed_df, summary = analyze_stock(
        clean_df,
        short_window=args.short_ma,
        long_window=args.long_ma,
    )
    bt_stats = run_sma_crossover_backtest(
        analyzed_df,
        short_col=f"SMA_{args.short_ma}",
        long_col=f"SMA_{args.long_ma}",
        fee_bps=args.fee_bps,
    )
    chart_paths = create_charts(
        analyzed_df,
        ticker=symbol,
        short_window=args.short_ma,
        long_window=args.long_ma,
    )
    report_paths = generate_report(
        ticker=symbol,
        source_label=source_label,
        df=analyzed_df,
        summary=summary,
        backtest_stats=bt_stats,
    )

    print("\n=== ANALYSIS SUMMARY ===")
    for k, v in summary.items():
        print(f"{k}: {v}")

    print("\n=== GENERATED FILES ===")
    for label, path in {**chart_paths, **report_paths}.items():
        print(f"{label}: {path}")


if __name__ == "__main__":
    main()