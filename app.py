import streamlit as st
import yfinance as yf
import requests
import pandas as pd

# Konfigurasi Halaman
st.set_page_config(page_title="TradeWise AI", layout="wide")

# FUNGSI CACHE (Mencegah Error Rate Limit)
@st.cache_data(ttl=3600)
def get_safe_data(ticker):
    try:
        df = yf.download(ticker, period="3mo", progress=False)
        stock = yf.Ticker(ticker)
        return df, stock.info
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
            with st.spinner("Memproses..."):
                df, _ = get_safe_data(ticker)
                if not df.empty and 'Close' in df.columns:
                    delta = df['Close'].diff()
                    gain = (delta.where(delta > 0, 0)).rolling(14).mean()
                    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
                    rsi = 100 - (100 / (1 + (gain / loss)))
                    st.line_chart(rsi)
                    val = float(rsi.iloc[-1])
                    st.metric("Skor RSI", f"{val:.2f}")
                else: st.warning("Data tidak tersedia atau server sibuk.")

    # FUNDAMENTAL & BERITA
    elif page == "Fundamental & Berita":
        st.title("📰 Fundamental & Berita")
        ticker = st.text_input("Cek Saham:", "AAPL")
        if st.button("Tampilkan"):
            _, info = get_safe_data(ticker)
            st.metric("P/E Ratio", info.get('trailingPE', 'N/A'))
            
            API_KEY = "a8f7e0c949134eea9863c652f02f8175"
            url = f"https://newsapi.org/v2/everything?q={ticker}&apiKey={API_KEY}&language=id&pageSize=3"
            try:
                res = requests.get(url, timeout=10).json()
                for art in res.get('articles', []):
                    st.write(f"**{art['title']}**")
                    st.markdown(f"[Baca]({art['url']})")
                    st.divider()
            except: st.error("Berita gagal dimuat.")
