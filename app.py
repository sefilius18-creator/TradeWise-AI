import streamlit as st
import yfinance as yf
import pandas as pd
from openai import OpenAI
from duckduckgo_search import DDGS

# Konfigurasi Halaman
st.set_page_config(page_title="TradeWise AI", layout="wide")

# CSS Transparan
st.markdown("""
    <style>
    .stApp { background: url('https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?q=80&w=2070'); background-size: cover; }
    .main > div { background-color: rgba(15, 23, 42, 0.9); padding: 2rem; border-radius: 15px; }
    h1, h2, h3 { color: #38bdf8 !important; }
    </style>
""", unsafe_allow_html=True)

# Fungsi Logika
def calculate_rsi(data, window=14):
    delta = data['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

# Sidebar
ticker = st.sidebar.text_input("Kode Saham (Contoh: BBCA.JK)", "BBCA.JK")
api_key = st.secrets.get("OPENAI_API_KEY", st.sidebar.text_input("OpenAI API Key:", type="password"))

st.title("📈 TradeWise AI")

tab1, tab2 = st.tabs(["🔍 News Sentiment", "📈 Technical Analysis"])

with tab1:
    if st.button("Analisis Berita"):
        if api_key:
            try:
                search = DDGS()
                results = search.text(f"{ticker} stock news", max_results=3)
                headlines = "\n".join([r['body'] for r in results])
                client = OpenAI(api_key=api_key)
                res = client.chat.completions.create(model="gpt-4o", messages=[{"role": "user", "content": f"Analisis sentimen {ticker}: {headlines}"}])
                st.session_state.sentimen_data = res.choices[0].message.content
                st.write(st.session_state.sentimen_data)
            except Exception as e: st.error(f"Error: {e}")
        else: st.warning("Masukkan API Key!")

with tab2:
    data = yf.download(ticker, period="3mo")
    # Pengecekan data yang lebih ketat
    if not data.empty and 'Close' in data.columns and len(data) > 14:
        rsi_series = calculate_rsi(data)
        val = rsi_series.iloc[-1]
        
        # Cek apakah val adalah angka (bukan NaN, bukan None, bukan tipe data salah)
        try:
            val_float = float(val)
            st.session_state.rsi_val = val_float
            st.line_chart(rsi_series)
            st.metric("RSI Saat Ini", f"{val_float:.2f}")
        except (ValueError, TypeError):
            st.error("Data teknikal sedang tidak valid untuk saham ini.")
    else:
        st.error("Data tidak ditemukan. Pastikan ticker benar (gunakan akhiran .JK untuk Indonesia).")

# Trading Advisor
if st.button("Generate Trading Summary"):
    if api_key and "sentimen_data" in st.session_state:
        client = OpenAI(api_key=api_key)
        res = client.chat.completions.create(model="gpt-4o", messages=[{"role": "user", "content": f"Analisis {ticker}. RSI: {st.session_state.rsi_val}. Sentimen: {st.session_state.sentimen_data}. Berikan rekomendasi."}])
        st.success(res.choices[0].message.content)
    else: st.error("Analisis sentimen belum dilakukan atau API Key kosong.")
