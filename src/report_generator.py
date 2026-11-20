"""
Report Generator Module.
Saves a detailed text analysis report and CSV summary metrics/data.
"""

from __future__ import annotations

from pathlib import Path
import pandas as pd


def generate_report(
    ticker: str,
    source_label: str,
    df: pd.DataFrame,
    summary: dict,
    backtest_stats: dict | None = None,
    reports_dir: str | Path = "reports",
    outputs_dir: str | Path = "outputs",
) -> dict[str, Path]:
    """Write human-readable report (.txt) and CSV exports (.csv)."""
    symbol = ticker.strip().upper()
    rep_dir = Path(reports_dir)
    out_dir = Path(outputs_dir)
    rep_dir.mkdir(parents=True, exist_ok=True)
    out_dir.mkdir(parents=True, exist_ok=True)

    report_txt_path = rep_dir / f"{symbol.lower()}_analysis_report.txt"
    summary_csv_path = rep_dir / f"{symbol.lower()}_summary_metrics.csv"
    series_csv_path = out_dir / f"{symbol.lower()}_analyzed_series.csv"

    lines = [
        "=" * 64,
        f"STOCK MARKET DATA ANALYZER REPORT — {symbol}",
        "=" * 64,
        f"Data Source          : {source_label}",
        f"Analysis Window      : {summary['start_date']} to {summary['end_date']} ({summary['trading_days']} trading days)",
        "",
        "--- PRICE & TREND SUMMARY ---",
        f"Starting Close Price : ${summary['start_price']:.2f}",
        f"Latest Close Price   : ${summary['end_price']:.2f}",
        f"Total Period Return  : {summary['total_return_pct']:+.2f}%",
        f"Period High          : ${summary['highest_price']:.2f} (on {summary['highest_price_date']})",
        f"Period Low           : ${summary['lowest_price']:.2f} (on {summary['lowest_price_date']})",
        f"Latest Short MA      : ${summary['latest_short_ma']:.2f}",
        f"Latest Long MA       : ${summary['latest_long_ma']:.2f}",
        f"Current Trend Regime : {summary['latest_trend']}",
        "",
        "--- RETURNS & RISK (VOLATILITY) SUMMARY ---",
        f"Avg Daily Return     : {summary['avg_daily_return_pct']:+.4f}%",
        f"Annualized Volatility: {summary['annualized_volatility_pct']:.2f}%",
        f"Max Drawdown         : {summary['max_drawdown_pct']:.2f}%",
        f"Annualized Sharpe    : {summary['sharpe_ratio']:.2f}",
        f"Best Single Day      : {summary['best_day_pct']:+.2f}% (on {summary['best_day_date']})",
        f"Worst Single Day     : {summary['worst_day_pct']:+.2f}% (on {summary['worst_day_date']})",
    ]

    if backtest_stats:
        lines.extend(
            [
                "",
                "--- OPTIONAL SMA CROSSOVER BACKTEST (LAGGED, WITH FEES) ---",
                f"Strategy Return      : {backtest_stats['total_return_pct']:+.2f}%",
                f"Strategy Max DD      : {backtest_stats['max_drawdown_pct']:.2f}%",
                f"Strategy Sharpe      : {backtest_stats['sharpe_ratio']:.2f}",
                f"Total Signals/Trades : {backtest_stats['trades']}",
                f"Trade Win Rate       : {backtest_stats['win_rate_pct']:.2f}%",
            ]
        )

    lines.extend(
        [
            "",
            "Disclaimer: Educational analysis only; not financial or investment advice.",
            "=" * 64,
        ]
    )

    report_txt_path.write_text("\n".join(lines), encoding="utf-8")
    pd.DataFrame([summary]).to_csv(summary_csv_path, index=False)

    export_df = df.copy()
    export_df.index.name = "Date"
    export_df.to_csv(series_csv_path)

    return {
        "report_txt": report_txt_path,
        "summary_csv": summary_csv_path,
        "series_csv": series_csv_path,
    }