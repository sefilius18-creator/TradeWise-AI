import streamlit as st
import yfinance as yf
import pandas as pd
from openai import OpenAI
from duckduckgo_search import DDGS

# 1. Konfigurasi Halaman
st.set_page_config(page_title="TradeWise AI", layout="wide", page_icon="📈")

# CSS untuk tampilan Profesional & Dark Mode
st.markdown("""
    <style>
    .stApp { background-color: #0f172a; color: white; }
    h1, h2, h3 { color: #38bdf8 !important; }
    .stButton>button { width: 100%; border-radius: 10px; background-color: #38bdf8; color: white; }
    </style>
""", unsafe_allow_html=True)

# 2. Fungsi Analisis
def calculate_rsi(data, window=14):
    delta = data['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def analyze_sentiment(ticker, api_key):
    try:
        search = DDGS()
        results = search.text(f"{ticker} stock news", max_results=3)
        headlines = "\n".join([r['body'] for r in results])
        client = OpenAI(api_key=api_key)
        prompt = f"Analisis sentimen berita berikut untuk saham {ticker}: {headlines}. Berikan Sentimen (Bullish/Bearish/Neutral), Skor (0-100), dan penjelasan singkat."
        response = client.chat.completions.create(model="gpt-4o", messages=[{"role": "user", "content": prompt}])
        return response.choices[0].message.content
    except Exception as e:
        return f"Gagal menganalisis: {e}"

# 3. Sidebar
st.sidebar.title("🛠 Konfigurasi")
ticker = st.sidebar.text_input("Kode Saham (Contoh: BBCA.JK)", "BBCA.JK")

# Menggunakan Streamlit Secrets jika tersedia, jika tidak, minta input manual
if "OPENAI_API_KEY" in st.secrets:
    api_key = st.secrets["OPENAI_API_KEY"]
else:
    api_key = st.sidebar.text_input("OpenAI API Key:", type="password")

# 4. Antarmuka Utama
st.title("📈 TradeWise AI")
tab1, tab2 = st.tabs(["🔍 News Sentiment", "📈 Technical Analysis"])

if "sentimen_data" not in st.session_state: st.session_state.sentimen_data = ""
if "rsi_val" not in st.session_state: st.session_state.rsi_val = 50

with tab1:
    st.header("Analisis Sentimen Berita")
    if st.button("Analisis Berita"):
        if api_key:
            with st.spinner("Menganalisis..."):
                st.session_state.sentimen_data = analyze_sentiment(ticker, api_key)
                st.markdown(st.session_state.sentimen_data)
        else: st.warning("Masukkan API Key di sidebar.")

with tab2:
    st.header("Analisis Teknikal (RSI)")
    data = yf.download(ticker, period="3mo")
    if not data.empty:
        rsi_series = calculate_rsi(data)
        st.session_state.rsi_val = rsi_series.iloc[-1]
        st.line_chart(rsi_series)
        st.metric("RSI Saat Ini", f"{st.session_state.rsi_val:.2f}")
    else: st.error("Data tidak ditemukan. Pastikan ticker benar.")

# 5. AI Trading Advisor
st.markdown("---")
st.header("✨ AI Trading Advisor")
if st.button("Generate Trading Summary"):
    if api_key and st.session_state.sentimen_data:
        client = OpenAI(api_key=api_key)
        prompt = f"Saham {ticker}. RSI: {st.session_state.rsi_val:.2f}. Sentimen: {st.session_state.sentimen_data}. Berikan rekomendasi BELI/JUAL/WAIT dan alasannya."
        res = client.chat.completions.create(model="gpt-4o", messages=[{"role": "user", "content": prompt}])
        st.success(res.choices[0].message.content)
    else: st.error("Lakukan analisis sentimen dan pastikan API Key terisi!")
