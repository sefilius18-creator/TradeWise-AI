import streamlit as st
import yfinance as yf
import requests
import pandas as pd

# 1. KONFIGURASI HALAMAN
st.set_page_config(page_title="TradeWise AI Pro", layout="wide")

# 2. FUNGSI DATA YANG AMAN (DENGAN CACHING)
@st.cache_data(ttl=3600)
def get_stock_data(ticker):
    try:
        df = yf.download(ticker, period="3mo", progress=False)
        ticker_info = yf.Ticker(ticker).info
        return df, ticker_info
    except Exception:
        return pd.DataFrame(), {}

# 3. SISTEM LOGIN
if "auth" not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    st.title("🔐 Login TradeWise AI")
    pwd = st.text_input("Masukkan Password:", type="password")
    if st.button("Login"):
        if pwd == "Sefilius18": st.session_state.auth = True; st.rerun()
        else: st.error("Password Salah!")
else:
    # 4. SIDEBAR NAVIGASI
    with st.sidebar:
        st.header("☰ Menu Utama")
        page = st.radio("Pilih Halaman:", ["Dashboard Analisis", "Fundamental & Berita"])
        if st.button("Logout"): st.session_state.auth = False; st.rerun()

    # 5. HALAMAN DASHBOARD ANALISIS
    if page == "Dashboard Analisis":
        st.title("📈 Dashboard Analisis")
        ticker = st.text_input("Kode Saham (contoh: AAPL atau BBCA.JK):", "AAPL")
        if st.button("Analisis"):
            with st.spinner("Mengolah data RSI..."):
                df, _ = get_stock_data(ticker)
                if not df.empty and 'Close' in df.columns:
                    # Kalkulasi RSI
                    delta = df['Close'].diff()
                    gain = (delta.where(delta > 0, 0)).rolling(14).mean()
                    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
                    rsi = 100 - (100 / (1 + (gain / loss)))
                    
                    st.line_chart(rsi)
                    # Mengambil nilai terakhir dengan aman
                    val = float(rsi.iloc[-1])
                    st.metric("Skor RSI Terkini", f"{val:.2f}")
                else: st.warning("Data tidak tersedia atau server sibuk.")

    # 6. HALAMAN FUNDAMENTAL & BERITA
    elif page == "Fundamental & Berita":
        st.title("📰 Fundamental & Berita")
        ticker = st.text_input("Masukkan Kode Saham:", "AAPL")
        if st.button("Tampilkan"):
            _, info = get_stock_data(ticker)
            st.metric("P/E Ratio", info.get('trailingPE', 'N/A'))
            
            # Berita dengan API
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
