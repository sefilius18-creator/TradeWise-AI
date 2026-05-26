import streamlit as st
import yfinance as yf
import pandas as pd
from openai import OpenAI
from duckduckgo_search import DDGS

# 1. Konfigurasi Halaman
st.set_page_config(page_title="TradeWise AI", layout="wide", page_icon="📈")

# CSS dengan Latar Belakang Grafik Saham (Overlay Transparan)
st.markdown("""
    <style>
    .stApp {
        background-image: url('https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?q=80&w=2070&auto=format&fit=crop');
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }
    .stApp::before {
        content: "";
        position: absolute;
        top: 0; left: 0; width: 100%; height: 100%;
        background-color: rgba(15, 23, 42, 0.9); /* Overlay gelap agar teks tetap terbaca */
        z-index: -1;
    }
    h1, h2, h3 { color: #38bdf8 !important; }
    .stButton>button { width: 100%; border-radius: 10px; background-color: #38bdf8; color: white; }
    .stMetric { background-color: rgba(30, 41, 59, 0.8); padding: 15px; border-radius: 10px; }
    </style>
""", unsafe_allow_html=True)

# 2. Fungsi Logika (tetap sama)
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
        prompt = f"Analisis sentimen berita untuk saham {ticker}: {headlines}. Berikan Sentimen, Skor (0-100), dan penjelasan singkat."
        response = client.chat.completions.create(model="gpt-4o", messages=[{"role": "user", "content": prompt}])
        return response.choices[0].message.content
    except Exception as e:
        return f"Gagal menganalisis: {e}"

# 3. Sidebar & Utama (tetap sama)
st.sidebar.title("🛠 Konfigurasi")
ticker = st.sidebar.text_input("Kode Saham (Contoh: BBCA.JK)", "BBCA.JK")
api_key = st.secrets.get("OPENAI_API_KEY", st.sidebar.text_input("OpenAI API Key:", type="password"))

st.title("📈 TradeWise AI")
tab1, tab2 = st.tabs(["🔍 News Sentiment", "📈 Technical Analysis"])

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
    if not data.empty and len(data) >= 14:
        rsi_series = calculate_rsi(data)
        current_rsi = rsi_series.iloc[-1]
        st.line_chart(rsi_series)
        st.metric("RSI Saat Ini", f"{float(current_rsi):.2f}")
    else:
        st.error("Data tidak ditemukan.")

st.markdown("---")
st.header("✨ AI Trading Advisor")
if st.button("Generate Trading Summary"):
    if api_key and "sentimen_data" in st.session_state:
        client = OpenAI(api_key=api_key)
        prompt = f"Saham {ticker}. RSI: {st.session_state.get('rsi_val', 50):.2f}. Sentimen: {st.session_state.sentimen_data}. Rekomendasi BELI/JUAL/WAIT?"
        res = client.chat.completions.create(model="gpt-4o", messages=[{"role": "user", "content": prompt}])
        st.success(res.choices[0].message.content)
