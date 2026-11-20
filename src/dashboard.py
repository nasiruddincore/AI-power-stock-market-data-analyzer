import numpy as np
import pandas as pd
import pydeck as pdk
import streamlit as st
import yfinance as yf

st.set_page_config(
    page_title="Stock Market Data Analyzer",
    page_icon="📈",
    layout="wide",
)

# Multi-Color Theme & Typography Styling
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&display=swap');

    .stApp {
        background: linear-gradient(135deg, #090d1e 0%, #1b1446 48%, #2a103c 100%);
        color: #f8fafc;
        font-family: 'Plus Jakarta Sans', 'Segoe UI', sans-serif;
    }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #16123b 0%, #2b1d5e 55%, #111827 100%);
        border-right: 1px solid rgba(168, 85, 247, 0.35);
    }

    .hero-box {
        background: linear-gradient(90deg, #2563eb 0%, #9333ea 52%, #ec4899 100%);
        padding: 22px 28px;
        border-radius: 18px;
        box-shadow: 0 12px 28px rgba(147, 51, 234, 0.35);
        border: 1px solid rgba(255, 255, 255, 0.22);
        margin-bottom: 18px;
    }

    .hero-title {
        font-size: 2rem;
        font-weight: 800;
        color: #ffffff;
        letter-spacing: -0.4px;
        margin: 0;
    }

    .hero-sub {
        font-size: 0.98rem;
        font-weight: 500;
        color: #fdf4ff;
        margin-top: 6px;
    }

    .banner-strip {
        background: linear-gradient(90deg, rgba(6, 182, 212, 0.18), rgba(168, 85, 247, 0.22), rgba(244, 63, 94, 0.18));
        border: 1px solid rgba(56, 189, 248, 0.45);
        border-radius: 12px;
        padding: 11px 16px;
        margin-bottom: 18px;
        font-size: 0.94rem;
        color: #e0f2fe;
    }

    .metric-card {
        border-radius: 16px;
        padding: 18px 20px;
        color: #ffffff;
        box-shadow: 0 10px 22px rgba(0, 0, 0, 0.32);
        border: 1px solid rgba(255, 255, 255, 0.2);
        transition: transform 0.2s ease;
    }

    .metric-card:hover {
        transform: translateY(-3px);
    }

    .metric-title {
        font-size: 0.82rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        opacity: 0.95;
    }

    .metric-val {
        font-size: 1.9rem;
        font-weight: 800;
        margin: 6px 0;
    }

    .metric-pill {
        display: inline-block;
        font-size: 0.8rem;
        font-weight: 600;
        background: rgba(255, 255, 255, 0.2);
        padding: 3px 10px;
        border-radius: 999px;
    }

    .grad-rose   { background: linear-gradient(135deg, #f43f5e 0%, #e11d48 100%); }
    .grad-cyan   { background: linear-gradient(135deg, #06b6d4 0%, #2563eb 100%); }
    .grad-violet { background: linear-gradient(135deg, #8b5cf6 0%, #6d28d9 100%); }
    .grad-emerald{ background: linear-gradient(135deg, #10b981 0%, #059669 100%); }

    .sec-title {
        font-size: 1.3rem;
        font-weight: 800;
        background: linear-gradient(90deg, #38bdf8, #c084fc, #f472b6, #fbbf24);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-top: 20px;
        margin-bottom: 10px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Hero Header
st.markdown(
    """
    <div class="hero-box">
        <div class="hero-title">📈 Stock Market Data Analyzer</div>
        <div class="hero-sub">Multi-Color Analytics • Moving Averages & Volatility • Interactive Market Map • Educational Demo</div>
    </div>
    """,
    unsafe_allow_html=True,
)

# Sidebar Controls
st.sidebar.markdown("## 🎛️ Market Controls")
ticker = st.sidebar.text_input("Ticker Symbol", value="AAPL").strip().upper()
period = st.sidebar.selectbox("Lookback Period", ["3mo", "6mo", "1y", "2y", "5y"], index=2)
short_win = st.sidebar.slider("Short SMA Window", 5, 50, 20, step=5)
long_win = st.sidebar.slider("Long SMA Window", 20, 200, 50, step=10)

hubs = {
    "New York (NYSE / NASDAQ)": (40.7069, -74.0113),
    "London (LSE)": (51.5155, -0.0922),
    "Mumbai (NSE / BSE)": (19.0607, 72.8362),
    "Tokyo (TSE)": (35.6828, 139.7769),
}
selected_hub = st.sidebar.selectbox("🗺️ Exchange / Market Map Hub", list(hubs.keys()))

if not ticker:
    st.stop()

# Fetch Data (yfinance with fallback simulation)
df = pd.DataFrame()
source = "yfinance"
try:
    raw = yf.download(ticker, period=period, auto_adjust=False, progress=False)
    if raw is not None and not raw.empty:
        if isinstance(raw.columns, pd.MultiIndex):
            raw.columns = [c[0] for c in raw.columns]
        raw = raw.reset_index()
        raw["Date"] = pd.to_datetime(raw["Date"]).dt.tz_localize(None)
        df = raw.dropna(subset=["Close"]).sort_values("Date").set_index("Date")
except Exception as exc:
    st.warning(f"yfinance unavailable ({exc}); using fallback simulation.")

if df.empty:
    source = "fallback_simulation"
    dates = pd.bdate_range(end=pd.Timestamp.today().normalize(), periods=252)
    rng = np.random.default_rng(42)
    close = 180.0 * np.cumprod(1.0 + rng.normal(0.0005, 0.015, size=len(dates)))
    df = pd.DataFrame({"Close": np.round(close, 2)}, index=dates)
    df.index.name = "Date"

df["Daily_Return_Pct"] = df["Close"].pct_change() * 100.0
s_col = f"SMA_{short_win}"
l_col = f"SMA_{long_win}"
df[s_col] = df["Close"].rolling(short_win, min_periods=1).mean()
df[l_col] = df["Close"].rolling(long_win, min_periods=1).mean()

latest_close = float(df["Close"].iloc[-1])
start_close = float(df["Close"].iloc[0])
total_ret = ((latest_close - start_close) / start_close) * 100.0
ann_vol = float(df["Close"].pct_change().dropna().std() * np.sqrt(252) * 100.0)
high_px = float(df["Close"].max())
low_px = float(df["Close"].min())
trend_label = "Uptrend" if df[s_col].iloc[-1] >= df[l_col].iloc[-1] else "Downtrend"

st.markdown(
    f"""
    <div class="banner-strip">
        📌 <b>Ticker:</b> {ticker} &nbsp;|&nbsp;
        🛰️ <b>Source:</b> {source} &nbsp;|&nbsp;
        📅 <b>Rows:</b> {len(df)} &nbsp;|&nbsp;
        🧭 <b>Trend ({s_col} vs {l_col}):</b> {trend_label}
    </div>
    """,
    unsafe_allow_html=True,
)

# 4 Colorful Gradient KPI Cards
k1, k2, k3, k4 = st.columns(4)
with k1:
    st.markdown(
        f"""
        <div class="metric-card grad-cyan">
            <div class="metric-title">💵 Latest Close</div>
            <div class="metric-val">${latest_close:.2f}</div>
            <div class="metric-pill">Return: {total_ret:+.2f}%</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
with k2:
    st.markdown(
        f"""
        <div class="metric-card grad-emerald">
            <div class="metric-title">🏔️ Period High</div>
            <div class="metric-val">${high_px:.2f}</div>
            <div class="metric-pill">Low: ${low_px:.2f}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
with k3:
    st.markdown(
        f"""
        <div class="metric-card grad-rose">
            <div class="metric-title">⚡ Annualized Vol</div>
            <div class="metric-val">{ann_vol:.2f}%</div>
            <div class="metric-pill">252-Day Basis</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
with k4:
    st.markdown(
        f"""
        <div class="metric-card grad-violet">
            <div class="metric-title">📊 {l_col}</div>
            <div class="metric-val">${float(df[l_col].iloc[-1]):.2f}</div>
            <div class="metric-pill">{s_col}: ${float(df[s_col].iloc[-1]):.2f}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# Colorful Charts + Interactive Map
st.markdown('<div class="sec-title">🎨 Price Trend, Moving Averages & Market Hub Map</div>', unsafe_allow_html=True)
left_col, right_col = st.columns([1.75, 1.25])

with left_col:
    st.markdown("**Price & Moving Averages**")
    st.line_chart(
        df[["Close", s_col, l_col]],
        color=["#38bdf8", "#f472b6", "#facc15"],
        height=310,
    )
    st.markdown("**Daily Return (%)**")
    st.bar_chart(
        df["Daily_Return_Pct"].dropna(),
        color="#a855f7",
        height=200,
    )

with right_col:
    st.markdown(f"**Interactive Map — {selected_hub}**")
    lat_val, lon_val = hubs[selected_hub]
    map_df = pd.DataFrame(
        {
            "lat": [lat_val],
            "lon": [lon_val],
            "hub": [selected_hub],
            "ticker": [ticker],
            "close": [f"${latest_close:.2f}"],
        }
    )

    halo = pdk.Layer(
        "ScatterplotLayer",
        data=map_df,
        get_position="[lon, lat]",
        get_color="[236, 72, 153, 85]",
        get_radius=12000,
    )
    beacon = pdk.Layer(
        "ScatterplotLayer",
        data=map_df,
        get_position="[lon, lat]",
        get_color="[56, 189, 248, 240]",
        get_line_color="[255, 255, 255, 255]",
        line_width_min_pixels=3,
        stroked=True,
        get_radius=4500,
        pickable=True,
    )
    view = pdk.ViewState(latitude=lat_val, longitude=lon_val, zoom=9.5, pitch=35)
    deck = pdk.Deck(
        map_style="https://basemaps.cartocdn.com/gl/voyager-gl-style/style.json",
        initial_view_state=view,
        layers=[halo, beacon],
        tooltip={"text": "📍 {hub}\n📈 {ticker}: {close}"},
    )
    st.pydeck_chart(deck, use_container_width=True)

with st.expander("📋 Recent Cleaned Data Table"):
    st.dataframe(df.tail(25), use_container_width=True)
