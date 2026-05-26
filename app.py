import streamlit as st
import yfinance as yf
import requests
import pandas as pd

st.set_page_config(page_title="TradeWise AI Pro", layout="wide")

# FUNGSI CACHE YANG AMAN (TTL 1 jam agar tidak diblokir Yahoo)
@st.cache_data(ttl=3600)
def get_data_safe(ticker):
    try:
        # Menggunakan .download() jauh lebih stabil daripada .Ticker().info
        df = yf.download(ticker, period="3mo", progress=False)
        info = yf.Ticker(ticker).info
        return df, info
    except Exception:
        return pd.DataFrame(), {}

# SISTEM LOGIN
if "auth" not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    st.title("🔐 TradeWise AI Login")
    pwd = st.text_input("Password:", type="password")
    if st.button("Login"):
        if pwd == "Sefilius18": st.session_state.auth = True; st.rerun()
        else: st.error("Password Salah!")
else:
    # SIDEBAR NAVIGASI
    with st.sidebar:
        st.header("☰ Menu Utama")
        page = st.radio("Navigasi:", ["Dashboard Analisis", "Fundamental & Berita"])
        if st.button("Logout"): st.session_state.auth = False; st.rerun()

    # DASHBOARD ANALISIS (RSI)
    if page == "Dashboard Analisis":
        st.title("📈 Dashboard Analisis")
        ticker = st.text_input("Kode Saham (Contoh: AAPL):", "AAPL")
        if st.button("Analisis"):
            with st.spinner("Mengambil data..."):
                df, _ = get_data_safe(ticker)
                if not df.empty and 'Close' in df.columns:
                    # Perhitungan RSI yang benar
                    delta = df['Close'].diff()
                    gain = (delta.where(delta > 0, 0)).rolling(14).mean()
                    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
                    rsi = 100 - (100 / (1 + (gain / loss)))
                    
                    st.line_chart(rsi)
                    # FIX: Pastikan mengambil nilai skalar dari Series
                    val = float(rsi.iloc[-1])
                    st.metric("Skor RSI", f"{val:.2f}")
                else:
                    st.error("Server sibuk/Blokir Yahoo. Coba lagi dalam 1 jam.")

    # FUNDAMENTAL & BERITA
    elif page == "Fundamental & Berita":
        st.title("📰 Fundamental & Berita")
        ticker = st.text_input("Kode Saham:", "AAPL")
        if st.button("Tampilkan"):
            _, info = get_data_safe(ticker)
            st.metric("P/E Ratio", info.get('trailingPE', 'N/A'))
            
            # API Berita
            API_KEY = "a8f7e0c949134eea9863c652f02f8175"
            url = f"https://newsapi.org/v2/everything?q={ticker}&apiKey={API_KEY}&language=id&pageSize=3"
            try:
                res = requests.get(url, timeout=10).json()
                st.subheader("Berita Terkini:")
                for art in res.get('articles', []):
                    st.write(f"**{art['title']}**")
                    st.markdown(f"[Baca Berita]({art['url']})")
                    st.divider()
            except: st.error("Gagal memuat berita.")
