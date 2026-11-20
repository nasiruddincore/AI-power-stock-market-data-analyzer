"""
Optional FastAPI Service for Stock Market Data Analyzer.
Run with: uvicorn api.app:app --reload
"""

from __future__ import annotations

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from src.analyzer import analyze_stock, run_sma_crossover_backtest
from src.cleaner import clean_stock_data
from src.data_loader import fetch_stock_data


app = FastAPI(title="Stock Market Data Analyzer API", version="1.0.0")


class BacktestRequest(BaseModel):
    ticker: str = "AAPL"
    start_date: str | None = None
    end_date: str | None = None
    period: str = "1y"
    short_window: int = 20
    long_window: int = 50
    fee_bps: float = 5.0


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/analyze/{ticker}")
def analyze(ticker: str, period: str = "1y", start_date: str | None = None, end_date: str | None = None) -> dict:
    try:
        raw, source = fetch_stock_data(ticker=ticker, start_date=start_date, end_date=end_date, period=period)
        cleaned = clean_stock_data(raw)
        enriched, summary = analyze_stock(cleaned)
        recent = enriched.tail(30).reset_index()
        recent["Date"] = recent["Date"].dt.strftime("%Y-%m-%d")
        return {
            "ticker": ticker.upper(),
            "source": source,
            "summary": summary,
            "recent_rows": recent[["Date", "Close", "SMA_20", "SMA_50", "Daily_Return_Pct"]].to_dict(orient="records"),
        }
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/backtest/sma")
def backtest(req: BacktestRequest) -> dict:
    try:
        raw, _ = fetch_stock_data(
            ticker=req.ticker,
            start_date=req.start_date,
            end_date=req.end_date,
            period=req.period,
        )
        cleaned = clean_stock_data(raw)
        enriched, _ = analyze_stock(cleaned, short_window=req.short_window, long_window=req.long_window)
        stats = run_sma_crossover_backtest(
            enriched,
            short_col=f"SMA_{req.short_window}",
            long_col=f"SMA_{req.long_window}",
            fee_bps=req.fee_bps,
        )
        return {"ticker": req.ticker.upper(), "stats": stats}
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc