import sqlite3
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from datetime import datetime

DB = "binance.db"

st.set_page_config(page_title="Binance Dashboard", page_icon="📈", layout="wide")
st.title("📈 Binance Dashboard")

conn = sqlite3.connect(DB)

# ── 1. SỐ DƯ ──────────────────────────────────────────────
st.subheader("💰 Số dư tài khoản (lần fetch gần nhất)")
df_bal = pd.read_sql("""
    SELECT asset, free, locked, free+locked AS total
    FROM balances
    WHERE fetched_at = (SELECT MAX(fetched_at) FROM balances)
    ORDER BY total DESC
""", conn)
st.dataframe(df_bal, use_container_width=True)

# ── 2. GIÁ COIN ────────────────────────────────────────────
st.subheader("💵 Giá coin (lần fetch gần nhất)")
df_price = pd.read_sql("""
    SELECT symbol, price, fetched_at
    FROM prices
    WHERE fetched_at = (SELECT MAX(fetched_at) FROM prices)
""", conn)

cols = st.columns(len(df_price))
for col, (_, row) in zip(cols, df_price.iterrows()):
    col.metric(label=row["symbol"], value=f"${row['price']:,.2f}")

# ── 3. CHART NẾN ───────────────────────────────────────────
st.subheader("🕯️ Chart nến")

symbols = pd.read_sql("SELECT DISTINCT symbol FROM klines", conn)["symbol"].tolist()
symbol = st.selectbox("Chọn coin", symbols)

df_k = pd.read_sql(f"""
    SELECT open_time, open, high, low, close, volume
    FROM klines
    WHERE symbol = '{symbol}' AND interval = '1h'
    ORDER BY open_time ASC
""", conn)

df_k["open_time"] = pd.to_datetime(df_k["open_time"].astype(float), unit="ms")

fig = go.Figure(data=[go.Candlestick(
    x=df_k["open_time"],
    open=df_k["open"], high=df_k["high"],
    low=df_k["low"],   close=df_k["close"],
)])
fig.update_layout(xaxis_rangeslider_visible=False, height=450)
st.plotly_chart(fig, use_container_width=True)

# ── 4. LỊCH SỬ TRADE ──────────────────────────────────────
st.subheader("📋 Lịch sử trade")
df_trades = pd.read_sql("""
    SELECT symbol,
           CASE WHEN is_buyer=1 THEN 'BUY' ELSE 'SELL' END AS side,
           price, qty, quote_qty,
           datetime(CAST(time AS INTEGER)/1000, 'unixepoch') AS time
    FROM trades
    ORDER BY time DESC
    LIMIT 50
""", conn)
st.dataframe(df_trades, use_container_width=True)

conn.close()
st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")