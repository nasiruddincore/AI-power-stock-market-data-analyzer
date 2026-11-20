# Stock Market Data Analyzer

A modular Python project that fetches historical stock market data (via `yfinance` with a local CSV fallback), cleans time-series records, computes daily returns, moving averages, volatility, and drawdowns, generates visualizations and summary reports, and provides optional FastAPI and Streamlit interfaces.

> **Disclaimer:** This project is created strictly for **educational and portfolio demonstration purposes**. It is **not** financial, investment, or trading advice.

## Problem Statement
Manually tracking stock prices, calculating daily returns and moving averages, and assessing price volatility across dozens or hundreds of trading days in spreadsheets is slow and error-prone. This project automates market data ingestion, cleaning, statistical/trend analysis, chart creation, and report generation in Python.

## Industry Relevance
Clean market data ingestion, time-series feature engineering, risk/return metrics, reproducible backtesting, APIs, and dashboards are core building blocks across **Python Developer**, **Data Analyst**, **Financial Analyst**, **Business Analyst**, and **FinTech** workflows.

## Features
- **Public Data + CSV Fallback:** Pulls historical OHLCV data using `yfinance` and falls back cleanly to a local CSV when offline or if a query returns empty.
- **Data Cleaning:** Parses dates, coerces numeric types, removes invalid or duplicate rows, and sorts chronologically.
- **Trend & Moving Averages:** Computes short and medium simple moving averages (`SMA_20`, `SMA_50`), period highs/lows, and trend classification.
- **Returns & Risk Analysis:** Calculates daily returns, best/worst trading days, annualized volatility, maximum drawdown, Sharpe ratio, and optional lagged SMA crossover backtest metrics.
- **Visualizations & Reports:** Saves price trend, moving average, and daily return charts plus a formatted `.txt` report and `.csv` outputs.
- **Optional API & Dashboard:** Includes a `FastAPI` service (`api/app.py`) and a `Streamlit` dashboard (`src/dashboard.py`).

## Tech Stack
- **Language & Core Data:** Python, `pandas`, `numpy`, `datetime`
- **Market Data & Indicators:** `yfinance`, `ta`
- **Visualization:** `matplotlib`, `seaborn`
- **Optional Web / API:** `fastapi`, `uvicorn`, `pydantic`, `streamlit`

## Folder Structure
```text
Stock-Market-Data-Analyzer/
├── data/
├── notebooks/
├── src/
├── api/
├── outputs/
├── images/
├── reports/
├── docs/
├── README.md
├── requirements.txt
├── .gitignore
└── main.py