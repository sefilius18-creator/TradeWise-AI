import streamlit as st
import yfinance as yf
import pandas as pd
from openai import OpenAI
from duckduckgo_search import DDGS

# 1. Konfigurasi Halaman
st.set_page_config(page_title="TradeWise AI", layout="wide", page_icon="📈")

# CSS: Menambahkan background transparan (card) untuk semua konten
st.markdown("""
    <style>
    .stApp {
        background-image: url('https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?q=80&w=2070&auto=format&fit=crop');
        background-size: cover;
        background-attachment: fixed;
    }
    /* Kotak transparan untuk semua elemen utama */
    .block-container {
        background-color: rgba(15, 23, 42, 0.85);
        padding: 2rem;
        border-radius: 15px;
    }
    h1, h2, h3 { color: #38bdf8 !important; }
    .stButton>button { width: 100%; border-radius: 10px; background-color: #38bdf8; color: white; }
    </style>
""", unsafe_allow_html=True)

# 2. Fungsi Logika
def calculate_rsi(data, window=14):
    delta = data['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

# 3. Sidebar
ticker = st.sidebar.text_input("Kode Saham (Contoh: BBCA.JK)", "BBCA.JK")
api_key = st.secrets.get("OPENAI_API_KEY", st.sidebar.text_input("OpenAI API Key:", type="password"))

# 4. Antarmuka Utama
st.title("📈 TradeWise AI")

# Gunakan session state untuk menyimpan nilai agar tidak error saat reload
if "rsi_val" not in st.session_state: st.session_state.rsi_val = 0.0

tab1, tab2 = st.tabs(["🔍 News Sentiment", "📈 Technical Analysis"])

with tab1:
    st.header("Analisis Sentimen Berita")
    if st.button("Analisis Berita"):
        if api_key:
            try:
                search = DDGS()
                results = search.text(f"{ticker} stock news", max_results=3)
                headlines = "\n".join([r['body'] for r in results])
                client = OpenAI(api_key=api_key)
                res = client.chat.completions.create(model="gpt-4o", messages=[{"role": "user", "content": f"Analisis sentimen {ticker}: {headlines}"}])
                st.session_state.sentimen_data = res.choices[0].message.content
                st.markdown(st.session_state.sentimen_data)
            except Exception as e:
                st.error(f"Error: {e}")
        else: st.warning("Masukkan API Key!")

with tab2:
    st.header("Analisis Teknikal (RSI)")
    data = yf.download(ticker, period="3mo")
    if not data.empty and len(data) >= 14:
        rsi_series = calculate_rsi(data)
        st.session_state.rsi_val = float(rsi_series.iloc[-1])
        st.line_chart(rsi_series)
        # Menghindari error dengan memastikan nilai adalah float
        st.metric("RSI Saat Ini", f"{st.session_state.rsi_val:.2f}")
    else:
        st.error("Data tidak ditemukan.")

# 5. Trading Advisor
if st.button("Generate Trading Summary"):
    if api_key and "sentimen_data" in st.session_state:
        client = OpenAI(api_key=api_key)
        res = client.chat.completions.create(model="gpt-4o", messages=[{"role": "user", "content": f"Saham {ticker}. RSI: {st.session_state.rsi_val}. Sentimen: {st.session_state.sentimen_data}. Berikan rekomendasi."}])
        st.success(res.choices[0].message.content)
    else: st.error("Lakukan analisis sentimen dulu.")
