import streamlit as st
import yfinance as yf
import requests
import pandas as pd

st.set_page_config(page_title="TradeWise AI", layout="wide")

# Menggunakan cache agar tidak kena Rate Limit
@st.cache_data(ttl=3600) # ttl=3600 detik (1 jam)
def get_safe_data(ticker):
    try:
        # Menggunakan yf.download lebih ringan daripada yf.Ticker().info
        df = yf.download(ticker, period="3mo", progress=False)
        return df
    except Exception:
        return pd.DataFrame()

# Navigasi Menu
menu = st.sidebar.radio("Menu", ["Dashboard", "Berita"])

if menu == "Dashboard":
    st.title("📈 Dashboard Analisis")
    ticker = st.text_input("Kode Saham (Contoh: AAPL):", "AAPL")
    
    if st.button("Analisis"):
        with st.spinner("Mengolah data..."):
            df = get_safe_data(ticker)
            if not df.empty and 'Close' in df.columns:
                # Perhitungan RSI
                delta = df['Close'].diff()
                gain = (delta.where(delta > 0, 0)).rolling(14).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
                rsi = 100 - (100 / (1 + (gain / loss)))
                
                st.line_chart(rsi)
                # Ambil nilai terakhir dengan .iloc[-1] agar tidak error 'Series'
                st.metric("Skor RSI", f"{float(rsi.iloc[-1]):.2f}")
            else:
                st.error("Gagal ambil data. Server sedang sibuk, tunggu 1 jam.")

elif menu == "Berita":
    st.title("📰 Berita Saham")
    ticker = st.text_input("Saham:", "AAPL")
    if st.button("Tampilkan Berita"):
        API_KEY = "a8f7e0c949134eea9863c652f02f8175"
        url = f"https://newsapi.org/v2/everything?q={ticker}&apiKey={API_KEY}&language=id&pageSize=3"
        try:
            res = requests.get(url, timeout=10).json()
            for art in res.get('articles', []):
                st.write(f"**{art['title']}**")
                st.markdown(f"[Baca]({art['url']})")
                st.divider()
        except:
            st.error("Gagal memuat berita.")
