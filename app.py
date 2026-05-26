import streamlit as st
import yfinance as yf
import requests
import pandas as pd

st.set_page_config(page_title="TradeWise AI", layout="wide")

# Fungsi Data Aman dengan Caching untuk mencegah Rate Limit
@st.cache_data(ttl=3600)
def get_stock_data(ticker):
    try:
        df = yf.download(ticker, period="3mo", progress=False)
        info = yf.Ticker(ticker).info
        return df, info
    except:
        return pd.DataFrame(), {}

# Sistem Login
if "auth" not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    st.title("🔐 Login TradeWise AI")
    pwd = st.text_input("Password:", type="password")
    if st.button("Login"):
        if pwd == "Sefilius18": st.session_state.auth = True; st.rerun()
        else: st.error("Password Salah!")
else:
    # Sidebar Navigasi
    with st.sidebar:
        st.header("Menu Utama")
        page = st.radio("Pilih Halaman:", ["Dashboard RSI", "Fundamental & Berita"])
        if st.button("Logout"): st.session_state.auth = False; st.rerun()

    # Halaman Dashboard RSI
    if page == "Dashboard RSI":
        st.title("📈 Analisis RSI")
        ticker = st.text_input("Kode Saham:", "AAPL")
        if st.button("Analisis"):
            df, _ = get_stock_data(ticker)
            if not df.empty and 'Close' in df.columns:
                delta = df['Close'].diff()
                gain = (delta.where(delta > 0, 0)).rolling(14).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
                rsi = 100 - (100 / (1 + (gain / loss)))
                st.line_chart(rsi)
                # Memastikan data adalah skalar sebelum dikonversi ke float
                val = float(rsi.iloc[-1].item() if hasattr(rsi.iloc[-1], 'item') else rsi.iloc[-1])
                st.metric("Skor RSI", f"{val:.2f}")
            else: st.warning("Data belum tersedia/Limit tercapai. Tunggu 1 jam.")

    # Halaman Fundamental & Berita
    elif page == "Fundamental & Berita":
        st.title("📰 Fundamental & Berita")
        ticker = st.text_input("Cek Saham:", "AAPL")
        if st.button("Tampilkan"):
            _, info = get_stock_data(ticker)
            st.metric("P/E Ratio", info.get('trailingPE', 'N/A'))
            
            API_KEY = "a8f7e0c949134eea9863c652f02f8175"
            url = f"https://newsapi.org/v2/everything?q={ticker}&apiKey={API_KEY}&language=id&pageSize=3"
            try:
                res = requests.get(url, timeout=10).json()
                for art in res.get('articles', []):
                    st.write(f"**{art['title']}**")
                    st.markdown(f"[Baca]({art['url']})")
                    st.divider()
            except: st.error("Gagal memuat berita.")
