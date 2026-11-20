# 📈 AI power + stock-market-data-analyzer

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-Data%20Analysis-150458?style=for-the-badge&logo=pandas&logoColor=white)
![NumPy](https://img.shields.io/badge/NumPy-Numerical%20Computing-013243?style=for-the-badge&logo=numpy&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-REST%20API-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![Matplotlib](https://img.shields.io/badge/Matplotlib-Charts-11557C?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Portfolio%20Ready-22C55E?style=for-the-badge)
![License](https://img.shields.io/badge/Type-Educational%20Project-A855F7?style=for-the-badge)

> **⚠️ Disclaimer:** This project is created strictly for **educational and portfolio demonstration purposes**. Nothing in this repository constitutes financial, investment, or trading advice.

---

## 🎯 Project Overview
**AI power + stock-market-data-analyzer** (**Stock Market Data Analyzer**) is a modular Python system that fetches public stock market data (`yfinance` with a local CSV fallback), cleans time-series data, calculates daily returns, moving averages, trend direction, volatility, and drawdowns, generates visual charts and summary reports, and provides optional `FastAPI` and `Streamlit` interfaces.

## 🧩 Problem Statement
Analyzing historical stock prices, daily percentage changes, moving averages, and volatility manually across large tables or spreadsheets is slow and error-prone. This project automates market data loading, cleaning, statistical and trend analysis, chart export, and report generation in a clean, repeatable Python workflow.

## 💼 Industry Relevance
Working with market time series, data validation, return/risk metrics, reproducible backtests, APIs, and interactive dashboards maps directly to skills valued in:
- 🐍 **Python Developer** roles
- 📊 **Data Analyst & Business Analyst** roles
- 💹 **Financial Analyst & FinTech** roles

---

## ✨ Key Features
- 📥 **Public Market Data + CSV Fallback:** Fetches historical OHLCV data using `yfinance` and falls back cleanly to local CSV/simulated sample data when offline or if a query returns empty.
- 🧹 **Data Cleaning:** Normalizes column names, parses timestamps, coerces numeric values, removes duplicates/invalid rows, and sorts chronologically.
- 📉 **Trend & Moving Averages:** Computes short and long Simple Moving Averages (`SMA_20`, `SMA_50`), period highs/lows, and trend classification.
- ⚡ **Returns & Risk Analysis:** Computes daily returns, best/worst single-day moves, annualized volatility, maximum drawdown, Sharpe ratio, and optional lagged SMA crossover backtest stats.
- 🖼️ **Visualizations & Reports:** Exports trend, moving average, and daily return charts plus `.txt` and `.csv` reports.
- 🎨 **Interactive Interfaces:** Includes a multi-color `Streamlit` dashboard (`src/dashboard.py`) with an interactive market hub map and an optional `FastAPI` service (`api/app.py`).

---

## 🛠️ Tech Stack
- **Core Language & Data:** Python, `pandas`, `numpy`, `datetime`
- **Market Data & Indicators:** `yfinance`, `ta`
- **Visualization & UI:** `matplotlib`, `seaborn`, `pydeck`, `streamlit`
- **API & Validation:** `fastapi`, `uvicorn`, `pydantic`

---

## 📁 Folder Structure

```text
stock-market-data-analyzer/
│
├── data/                  # Sample/fallback CSV files & local data
├── notebooks/             # Exploratory Jupyter notebooks
├── src/                   # Core Python modules (data_loader, cleaner, analyzer, visualizer, report_generator, dashboard)
├── api/                   # Optional FastAPI backend (app.py)
├── outputs/               # Generated CSV series and chart exports
├── images/                # Saved PNG charts and proof screenshots
├── reports/               # Generated summary reports (.txt and .csv)
├── docs/                  # Project notes and documentation
├── README.md              # Project documentation
├── requirements.txt       # Python dependencies
├── .gitignore             # Ignored files and folders
└── main.py                # Main CLI runner

💻 PowerShell Setup & Run Commands

    Tip: Using python -m pip, python -m streamlit, and python -m uvicorn avoids Windows Application Control policies that can block standalone .exe launchers in Scripts\.

1. Create Virtual Environment & Install Dependencies (PowerShell)
PowerShell

python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

2. Run the CLI Analysis Pipeline (PowerShell)
PowerShell

# Run 1-year analysis for AAPL
python main.py --ticker AAPL --period 1y

# Run custom date range for MSFT
python main.py --ticker MSFT --start 2024-01-01 --end 2026-11-01

3. Run the Streamlit Dashboard (PowerShell)
PowerShell

python -m streamlit run src/dashboard.py

4. Run the Optional FastAPI Backend (PowerShell)
PowerShell

python -m uvicorn api.app:app --reload

📊 Sample Output

When you run main.py, the project prints key metrics to the terminal and writes output files:

    Console Summary: Start/end close price, total period return, period high/low, moving averages, trend label, daily return average, annualized volatility, and max drawdown.

    Reports: reports/<ticker>_analysis_report.txt and reports/<ticker>_summary_metrics.csv.

    Tabular Data: outputs/<ticker>_analyzed_series.csv.

    Charts: images/<ticker>_trend.png, images/<ticker>_moving_averages.png, and images/<ticker>_daily_returns.png.

🖼️ Screenshots & Visuals

    images/aapl_trend.png — Closing price and daily price range trend

    images/aapl_moving_averages.png — Closing price with short and long moving averages

    images/aapl_daily_returns.png — Daily return bars and return distribution histogram

🎓 Learning Outcomes

    Built a modular Python pipeline separating data fetching, cleaning, analytics, visualization, reporting, API serving, and dashboard UI.

    Handled real-world data edge cases such as missing values, unsorted dates, and fallback data sources.

    Calculated financial return, trend, volatility, and drawdown metrics and presented them clearly for coursework and GitHub proof of work.
