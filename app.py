import streamlit as st
import yfinance as yf
import requests
import pandas as pd

st.set_page_config(page_title="TradeWise AI Pro", layout="wide")

# FUNGSI CACHE (Durasinya diperpanjang untuk mencegah pemblokiran oleh Yahoo)
@st.cache_data(ttl=3600)
def fetch_stock_data(ticker):
    try:
        # Menggunakan yf.download lebih stabil dibanding Ticker().info
        df = yf.download(ticker, period="3mo", progress=False)
        return df
    except Exception:
        return pd.DataFrame()

# SISTEM LOGIN
if "auth" not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    st.title("🔐 TradeWise AI Login")
    pwd = st.text_input("Password:", type="password")
    if st.button("Login"):
        if pwd == "Sefilius18": st.session_state.auth = True; st.rerun()
        else: st.error("Password Salah!")
else:
    # SIDEBAR
    with st.sidebar:
        st.header("☰ Menu Utama")
        page = st.radio("Navigasi:", ["Dashboard Analisis", "Berita Saham"])
        if st.button("Logout"): st.session_state.auth = False; st.rerun()

    # DASHBOARD ANALISIS
    if page == "Dashboard Analisis":
        st.title("📈 Dashboard Analisis")
        ticker = st.text_input("Kode Saham (Contoh: AAPL atau BBCA.JK):", "AAPL")
        
        if st.button("Analisis"):
            with st.spinner("Mengolah data..."):
                df = fetch_stock_data(ticker)
                if not df.empty and 'Close' in df.columns:
                    # Perhitungan RSI yang aman dari error Series
                    close = df['Close']
                    delta = close.diff()
                    gain = (delta.where(delta > 0, 0)).rolling(14).mean()
                    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
                    rsi = 100 - (100 / (1 + (gain / loss)))
                    
                    st.line_chart(rsi)
                    
                    # Mengambil nilai terakhir dengan aman
                    val = float(rsi.iloc[-1])
                    st.metric("Skor RSI", f"{val:.2f}")
                    
                    if val < 30: st.success("STATUS: OVERSOLD (Potensi Beli)")
                    elif val > 70: st.error("STATUS: OVERBOUGHT (Potensi Jual)")
                    else: st.info("STATUS: NETRAL")
                else:
                    st.warning("Data tidak tersedia atau server sedang sibuk. Tunggu 1 menit lalu coba lagi.")

    # BERITA (BAHASA INDONESIA)
    elif page == "Berita Saham":
        st.title("📰 Berita Saham")
        ticker = st.text_input("Saham:", "AAPL")
        if st.button("Tampilkan Berita"):
            API_KEY = "a8f7e0c949134eea9863c652f02f8175"
            url = f"https://newsapi.org/v2/everything?q={ticker}&apiKey={API_KEY}&language=id&pageSize=3"
            try:
                res = requests.get(url, timeout=10).json()
                articles = res.get('articles', [])
                if articles:
                    for art in articles:
                        st.write(f"**{art['title']}**")
                        st.markdown(f"[Baca Berita]({art['url']})")
                        st.divider()
                else:
                    st.warning("Tidak ada berita Bahasa Indonesia ditemukan.")
            except:
                st.error("Gagal memuat berita. Periksa koneksi atau coba saham lain.")
