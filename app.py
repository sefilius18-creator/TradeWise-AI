import streamlit as st
import yfinance as yf
import requests
import pandas as pd

# Konfigurasi Halaman
st.set_page_config(page_title="TradeWise AI", layout="wide")

# Fungsi Data dengan Penanganan Error yang Kuat
@st.cache_data(ttl=3600)
def get_data(ticker):
    try:
        df = yf.download(ticker, period="6mo", progress=False)
        info = yf.Ticker(ticker).info
        return df, info
    except Exception:
        return pd.DataFrame(), {}

# --- SISTEM NAVIGASI ---
st.sidebar.title("☰ Menu Utama")
menu = st.sidebar.radio("Pilih Halaman:", ["Dashboard RSI", "Fundamental & Berita"])

# --- HALAMAN 1: DASHBOARD RSI ---
if menu == "Dashboard RSI":
    st.title("📈 Analisis RSI")
    ticker = st.text_input("Kode Saham (Contoh: AAPL):", "AAPL")
    if st.button("Analisis"):
        df, _ = get_data(ticker)
        if not df.empty and 'Close' in df.columns:
            # Perhitungan RSI
            delta = df['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
            rsi = 100 - (100 / (1 + (gain / loss)))
            
            st.line_chart(rsi)
            
            # Perbaikan TypeError: Memastikan nilai adalah angka
            val = rsi.iloc[-1]
            if hasattr(val, 'item'): val = val.item() # Konversi dari series ke angka
            
            st.metric("Skor RSI Terkini", f"{float(val):.2f}")
            
            # Logika Rekomendasi
            if val < 30: st.success("STATUS: OVERSOLD. Peluang Beli.")
            elif val > 70: st.error("STATUS: OVERBOUGHT. Peluang Jual.")
            else: st.info("STATUS: NETRAL.")
        else:
            st.warning("Data tidak tersedia. Coba kode saham lain (Contoh: BBCA.JK atau AAPL).")

# --- HALAMAN 2: FUNDAMENTAL & BERITA ---
elif menu == "Fundamental & Berita":
    st.title("📰 Fundamental & Berita")
    ticker = st.text_input("Cek Saham:", "AAPL")
    if st.button("Tampilkan"):
        _, info = get_data(ticker)
        if info:
            st.metric("P/E Ratio", info.get('trailingPE', 'N/A'))
            st.metric("Market Cap", f"{info.get('marketCap', 0)/1e9:.2f} B")
            
            st.subheader("Berita Terkini:")
            API_KEY = "a8f7e0c949134eea9863c652f02f8175"
            url = f"https://newsapi.org/v2/everything?q={ticker}&apiKey={API_KEY}&language=id&pageSize=3"
            try:
                res = requests.get(url, timeout=10).json()
                if 'articles' in res:
                    for art in res['articles']:
                        st.write(f"**{art['title']}**")
                        st.markdown(f"[Baca]({art['url']})")
                        st.divider()
                else:
                    st.info("Tidak ada berita ditemukan.")
            except Exception:
                st.error("Gagal memuat berita.")
        else:
            st.warning("Data fundamental tidak ditemukan untuk saham tersebut.")
