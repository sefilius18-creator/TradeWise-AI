import streamlit as st
import yfinance as yf
import pandas as pd
from openai import OpenAI
from duckduckgo_search import DDGS

# Konfigurasi Halaman
st.set_page_config(page_title="TradeWise AI", layout="wide")

# CSS: Kotak hitam transparan untuk menjamin kontras teks
st.markdown("""
    <style>
    .stApp { background: url('https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?q=80&w=2070'); background-size: cover; }
    .main > div { 
        background-color: rgba(0, 0, 0, 0.85); 
        padding: 2rem; 
        border-radius: 15px; 
        color: white !important;
    }
    h1, h2, h3, .stMarkdown, .stMetric { color: #ffffff !important; }
    .stButton>button { width: 100%; background-color: #38bdf8 !important; color: black !important; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# Fungsi RSI yang Aman
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

if "rsi_val" not in st.session_state: st.session_state.rsi_val = 50.0
if "sentimen_data" not in st.session_state: st.session_state.sentimen_data = ""

tab1, tab2 = st.tabs(["🔍 News Sentiment", "📈 Technical Analysis"])

with tab1:
    if st.button("Analisis Berita"):
        if not api_key: st.error("Masukkan API Key di sidebar!")
        else:
            try:
                results = DDGS().text(f"{ticker} stock news", max_results=3)
                headlines = "\n".join([r['body'] for r in results])
                client = OpenAI(api_key=api_key)
                res = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "user", "content": f"Analisis sentimen {ticker}: {headlines}"}])
                st.session_state.sentimen_data = res.choices[0].message.content
                st.write(st.session_state.sentimen_data)
            except Exception as e: st.error(f"Error AI: {e}")

with tab2:
    try:
        df = yf.download(ticker, period="3mo", progress=False)
        # PERBAIKAN: Cek .empty dengan aman
        if df is not None and not df.empty and 'Close' in df.columns and len(df) > 14:
            rsi = calculate_rsi(df)
            val = rsi.iloc[-1]
            
            # PERBAIKAN: Pastikan val bukan NaN sebelum ditampilkan
            if pd.notnull(val):
                st.session_state.rsi_val = float(val)
                st.line_chart(rsi)
                st.metric("RSI Saat Ini", f"{st.session_state.rsi_val:.2f}")
            else:
                st.error("Data RSI tidak valid (mungkin saham baru).")
        else:
            st.error("Data tidak ditemukan. Pastikan ticker benar (contoh: BBCA.JK).")
    except Exception as e:
        st.error(f"Gagal memuat data teknikal.")

if st.button("Generate Trading Summary"):
    if api_key and st.session_state.sentimen_data:
        try:
            client = OpenAI(api_key=api_key)
            res = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "user", "content": f"RSI: {st.session_state.rsi_val:.2f}. Sentimen: {st.session_state.sentimen_data}. Rekomendasi?"}])
            st.success(res.choices[0].message.content)
        except Exception as e: st.error(f"Gagal generate: {e}")
    else: st.error("Lakukan analisis berita dulu.")
