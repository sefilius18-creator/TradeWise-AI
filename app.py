import streamlit as st
import yfinance as yf
import requests
import pandas as pd

# Konfigurasi Halaman
st.set_page_config(page_title="TradeWise AI", layout="wide")

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
    st.title("🔐 Login")
    pwd = st.text_input("Password:", type="password")
    if st.button("Login"):
        if pwd == "Sefilius18": st.session_state.auth = True; st.rerun()
        else: st.error("Password Salah!")
else:
    # --- NAVIGASI ---
    st.sidebar.title("Menu Utama")
    menu = st.sidebar.radio("Pilih Halaman:", ["Dashboard RSI", "Fundamental & Berita"])
    if st.sidebar.button("Logout"): st.session_state.auth = False; st.rerun()

    if menu == "Dashboard RSI":
        st.title("📈 Analisis RSI")
        ticker = st.text_input("Kode Saham:", "AAPL")
        if st.button("Analisis"):
            df, _ = get_data(ticker)
            if not df.empty and 'Close' in df.columns:
                delta = df['Close'].diff()
                gain = (delta.where(delta > 0, 0)).rolling(14).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
                rsi = 100 - (100 / (1 + (gain / loss)))
                
                # PERBAIKAN: Mengambil nilai scalar dengan aman
                val = rsi.iloc[-1]
                if hasattr(val, 'item'): val = val.item()
                
                st.line_chart(rsi)
                st.metric("Skor RSI", f"{float(val):.2f}")
            else: st.error("Data tidak tersedia.")

    elif menu == "Fundamental & Berita":
        st.title("📰 Fundamental & Berita")
        ticker = st.text_input("Cek Saham:", "AAPL")
        if st.button("Tampilkan"):
            _, info = get_data(ticker)
            st.metric("P/E Ratio", info.get('trailingPE', 'N/A'))
            
            # PERBAIKAN BERITA: Cek apakah ada data
            API_KEY = "a8f7e0c949134eea9863c652f02f8175"
            url = f"https://newsapi.org/v2/everything?q={ticker}&apiKey={API_KEY}&language=id&pageSize=3"
            try:
                res = requests.get(url, timeout=10).json()
                articles = res.get('articles', [])
                if articles:
                    for art in articles:
                        st.write(f"### {art['title']}")
                        st.markdown(f"[Baca Sumber]({art['url']})")
                else:
                    st.info("Berita tidak ditemukan untuk kode ini.")
            except: st.error("Gagal memuat berita dari API.")
