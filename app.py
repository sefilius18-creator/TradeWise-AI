import streamlit as st
import yfinance as yf
import requests
import pandas as pd

# Konfigurasi
st.set_page_config(page_title="TradeWise AI", layout="wide")

# Fungsi Data Aman
@st.cache_data(ttl=3600)
def get_data(ticker):
    try:
        df = yf.download(ticker, period="6mo", progress=False)
        info = yf.Ticker(ticker).info
        return df, info
    except: return pd.DataFrame(), {}

# --- SISTEM LOGIN ---
if "auth" not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    st.title("🔐 TradeWise AI Pro")
    pwd = st.text_input("Password:", type="password")
    if st.button("Login"):
        if pwd == "Sefilius18": st.session_state.auth = True; st.rerun()
        else: st.error("Password Salah!")
else:
    # --- NAVIGASI SIDEBAR (Dibuat permanen agar tidak hilang) ---
    st.sidebar.title("☰ Menu Utama")
    menu = st.sidebar.radio("Navigasi:", ["Dashboard Analisis", "Fundamental", "Berita Saham"])
    if st.sidebar.button("Logout"): st.session_state.auth = False; st.rerun()

    # --- 1. DASHBOARD ANALISIS ---
    if menu == "Dashboard Analisis":
        st.title("📈 Analisis Teknikal RSI")
        ticker = st.text_input("Kode Saham:", "AAPL")
        if st.button("Analisis RSI"):
            df, _ = get_data(ticker)
            if not df.empty and 'Close' in df.columns:
                delta = df['Close'].diff()
                gain = (delta.where(delta > 0, 0)).rolling(14).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
                rsi = 100 - (100 / (1 + (gain / loss)))
                
                # Konversi ke angka tunggal untuk menghindari TypeError
                val = float(rsi.iloc[-1].item() if hasattr(rsi.iloc[-1], 'item') else rsi.iloc[-1])
                
                st.line_chart(rsi)
                st.metric("Skor RSI", f"{val:.2f}")
                
                if val < 30: st.success("STATUS: OVERSOLD. Rekomendasi: **PELUANG BELI**")
                elif val > 70: st.error("STATUS: OVERBOUGHT. Rekomendasi: **PELUANG JUAL / KOREKSI**")
                else: st.info("STATUS: NETRAL. Rekomendasi: **WAIT AND SEE**")
            else: st.warning("Data belum tersedia. Tunggu 1 jam.")

    # --- 2. FUNDAMENTAL ---
    elif menu == "Fundamental":
        st.title("📊 Data Fundamental")
        ticker = st.text_input("Cek Saham:", "AAPL")
        if st.button("Tampilkan Fundamental"):
            _, info = get_data(ticker)
            if info:
                st.metric("P/E Ratio", info.get('trailingPE', 'N/A'))
                st.metric("Market Cap", f"{info.get('marketCap', 0)/1e9:.2f} B")
            else: st.error("Data Fundamental tidak ditemukan.")

    # --- 3. BERITA SAHAM ---
    elif menu == "Berita Saham":
        st.title("📰 Berita Terkini")
        ticker = st.text_input("Cari Berita:", "AAPL")
        if st.button("Muat Berita"):
            API_KEY = "a8f7e0c949134eea9863c652f02f8175"
            url = f"https://newsapi.org/v2/everything?q={ticker}&apiKey={API_KEY}&language=id&pageSize=3"
            try:
                res = requests.get(url, timeout=10).json()
                for art in res.get('articles', []):
                    st.write(f"### {art['title']}")
                    st.write(art['description'])
                    st.markdown(f"[Baca Sumber Asli]({art['url']})")
                    st.divider()
            except: st.error("Berita gagal dimuat.")
