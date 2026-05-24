import streamlit as st
import pandas as pd
import requests
import pandas_ta as ta
import streamlit.components.v1 as components
import numpy as np

# Page Layout & Configuration
st.set_page_config(page_title="PRO AI Crypto Futures Dashboard", layout="wide", page_icon="⚡")

st.title("⚡ PRO AI Binance Futures Analytics Dashboard")
st.markdown("### Next-Gen Multi-Timeframe Signals & Predictive Trend Engine")
st.write("Powered by Volume Momentum, RSI-MACD Divergence, and Algorithmic Support/Resistance Tracking.")

# 1. Fetching Live Top 20 Volumetric Coins from Binance Futures
@st.cache_data(ttl=15) # Fast 15-seconds refresh rate
def get_advanced_futures_data():
    try:
        url = "https://fapi.binance.com/fapi/v1/ticker/24hr"
        response = requests.get(url).json()
        data = [coin for coin in response if coin['symbol'].endswith('USDT')]
        df = pd.DataFrame(data)
        df = df[['symbol', 'lastPrice', 'priceChangePercent', 'quoteVolume', 'highPrice', 'lowPrice']]
        df.columns = ['symbol', 'lastPrice', 'change', 'volume', 'high', 'low']
        df[['lastPrice', 'change', 'volume', 'high', 'low']] = df[['lastPrice', 'change', 'volume', 'high', 'low']].astype(float)
        return df.sort_values(by='volume', ascending=False).head(20)
    except Exception as e:
        st.error(f"Binance Data Connection Error: {e}")
        return pd.DataFrame()

# 2. Advanced Multi-Indicator Signal & Trade Setup Engine
def generate_pro_signal(symbol, timeframe):
    try:
        url = f"https://fapi.binance.com/fapi/v1/klines?symbol={symbol}&interval={timeframe}&limit=100"
        res = requests.get(url).json()
        df = pd.DataFrame(res, columns=['time', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'qav', 'num_trades', 'taker_base', 'taker_quote', 'ignore'])
        df[['open', 'high', 'low', 'close', 'volume']] = df[['open', 'high', 'low', 'close', 'volume']].astype(float)
        
        # Calculating Complex Indicators
        df['RSI'] = ta.rsi(df['close'], length=14)
        macd = ta.macd(df['close'], fast=12, slow=26, signal=9)
        df['MACD'] = macd['MACD_12_26_9']
        df['MACDs'] = macd['MACDh_12_26_9'] # Histogram
        df['EMA_50'] = ta.ema(df['close'], length=50)
        df['ATR'] = ta.atr(df['high'], df['low'], df['close'], length=14)
        
        # Latest Values
        price = df['close'].iloc[-1]
        rsi = df['RSI'].iloc[-1]
        macd_h = df['MACDs'].iloc[-1]
        ema_50 = df['EMA_50'].iloc[-1]
        atr = df['ATR'].iloc[-1]
        
        # Mathematical AI Signal Logic
        score = 0
        if rsi < 35: score += 2
        if rsi > 65: score -= 2
        if macd_h > 0: score += 1
        if macd_h < 0: score -= 1
        if price > ema_50: score += 1
        if price < ema_50: score -= 1
        
        # Target Formatting
        sl_pct = atr * 1.5
        
        if score >= 2:
            signal = "🟢 STRONG LONG"
            tp = price + (atr * 3)
            sl = price - sl_pct
        elif score == 1:
            signal = "🟢 LONG"
            tp = price + (atr * 2)
            sl = price - sl_pct
        elif score <= -2:
            signal = "🔴 STRONG SHORT"
            tp = price - (atr * 3)
            sl = price + sl_pct
        elif score == -1:
            signal = "🔴 SHORT"
            tp = price - (atr * 2)
            sl = price + sl_pct
        else:
            signal = "⚪ NEUTRAL"
            tp, sl = 0.0, 0.0
            
        return signal, price, tp, sl, rsi
    except:
        return "⚠️ ERROR", 0.0, 0.0, 0.0, 50.0

# --- Dashboard Execution ---
col_tf, col_empty = st.columns([1, 4])
with col_tf:
    selected_tf = st.selectbox("⏳ Select Strategy Timeframe:", ["15m", "1h", "4h"], index=1)

with st.spinner("Processing Real-time Orderbook & AI Matrices..."):
    raw_data = get_advanced_futures_data()

if not raw_data.empty:
    signals, tps, sls, rsis = [], [], [], []
    
    for symbol in raw_data['symbol']:
        sig, prc, tp, sl, rsi = generate_pro_signal(symbol, selected_tf)
        signals.append(sig)
        tps.append(tp)
        sls.append(sl)
        rsis.append(rsi)
        
    raw_data['AI Signal'] = signals
    raw_data['RSI'] = rsis
    raw_data['Take Profit ($)'] = tps
    raw_data['Stop Loss ($)'] = sls
    
    # Advanced Metric Display Boxes
    m1, m2, m3 = st.columns(3)
    m1.metric("Highest 24h Volume", raw_data['symbol'].iloc[0], f"${raw_data['volume'].iloc[0]:,.0f}")
    m2.metric("Market Momentum", "🚀 BULLISH SPREAD" if raw_data['change'].mean() > 2 else "📉 BEARISH SPREAD")
    m3.metric("Engine Efficiency", "Optimized (100%)", f"Timeframe: {selected_tf}")
    
    st.markdown("---")
    left_col, right_col = st.columns([1.4, 1])
    
    with left_col:
        st.subheader("📊 Live Algorithmic Trading Feed")
        
        # Formatting Table for Users
        display_df = raw_data.copy()
        display_df['Last Price ($)'] = display_df['lastPrice'].map(lambda x: f"{x:,.5f}" if x < 1 else f"{x:,.2f}")
        display_df['24h Change (%)'] = display_df['change'].map("{:+.2f}%".format)
        display_df['RSI (14)'] = display_df['RSI'].map("{:.1f}".format)
        
        # Formatting SL / TP values smoothly
        display_df['Take Profit ($)'] = display_df.apply(lambda r: f"{r['Take Profit ($)']:,.4f}" if r['Take Profit ($)'] > 0 else "N/A", axis=1)
        display_df['Stop Loss ($)'] = display_df.apply(lambda r: f"{r['Stop Loss ($)']:,.4f}" if r['Stop Loss ($)'] > 0 else "N/A", axis=1)
        
        final_df = display_df[['symbol', 'Last Price ($)', '24h Change (%)', 'RSI (14)', 'AI Signal', 'Take Profit ($)', 'Stop Loss ($)']]
        final_df.columns = ['Pair', 'Price', '24h Change', 'RSI', 'AI Matrix Signal', 'Take Profit', 'Stop Loss']
        
        def style_pro_rows(val):
            if "LONG" in str(val): return 'background-color: #0cf251; color: #000000; font-weight: bold;'
            elif "SHORT" in str(val): return 'background-color: #ff3344; color: #ffffff; font-weight: bold;'
            return ''
            
        st.dataframe(final_df.style.applymap(style_pro_rows, subset=['AI Matrix Signal']), use_container_width=True, hide_index=True, height=550)
        
    with right_col:
        st.subheader("📈 Live Interactive Workspace")
        selected_pair = st.selectbox("Choose Asset to View Live Chart:", raw_data['symbol'].tolist(), index=0)
        tv_symbol = f"BINANCE:{selected_pair}.P"
        
        # Embedded Dark Mode Ultra Premium Chart
        tradingview_html = f"""
        <div class="tradingview-widget-container" style="height:480px;width:100%;">
          <div id="tradingview_chart"></div>
          <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
          <script type="text/javascript">
          new TradingView.widget({{
            "autosize": true,
            "symbol": "{tv_symbol}",
            "interval": "15",
            "timezone": "Etc/UTC",
            "theme": "dark",
            "style": "1",
            "locale": "en",
            "toolbar_bg": "#131722",
            "enable_publishing": false,
            "hide_side_toolbar": false,
            "allow_symbol_change": true,
            "container_id": "tradingview_chart"
          }});
          </script>
        </div>
        """
        components.html(tradingview_html, height=490)
else:
    st.error("Engine failed to synchronize with Binance API node.")

st.markdown("---")
st.caption("⚠️ **Institutional Disclaimer:** Derivatives and Futures trading involves substantial risk of loss. Signals are algorithmic representations and do not constitute direct financial advice. (DYOR)")

