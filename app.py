import streamlit as st
import yfinance as yf
import requests

st.set_page_config(page_title="TradeWise AI", layout="wide")

# 1. CACHE PALING AMAN (Menyimpan data selama 24 jam agar tidak memanggil Yahoo Finance berkali-kali)
@st.cache_data(ttl=86400)
def get_safe_data(ticker):
    # Menggunakan download() lebih stabil daripada Ticker().info
    df = yf.download(ticker, period="3mo", progress=False)
    return df

# 2. SISTEM LOGIN
if "auth" not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    st.title("🔐 Login")
    pwd = st.text_input("Password:", type="password")
    if st.button("Login") and pwd == "Sefilius18": 
        st.session_state.auth = True; st.rerun()
else:
    # 3. SIDEBAR
    with st.sidebar:
        st.header("☰ Menu")
        page = st.radio("Navigasi:", ["Analisis RSI", "Berita Saham"])
        if st.button("Logout"): st.session_state.auth = False; st.rerun()

    # 4. ANALISIS RSI
    if page == "Analisis RSI":
        st.title("📈 Analisis RSI")
        ticker = st.text_input("Kode Saham (contoh: AAPL):", "AAPL")
        if st.button("Analisis"):
            df = get_safe_data(ticker)
            if not df.empty:
                delta = df['Close'].diff()
                gain = (delta.where(delta > 0, 0)).rolling(14).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
                rsi = 100 - (100 / (1 + (gain / loss)))
                st.line_chart(rsi)
                # Ambil nilai terakhir dengan aman
                val = float(rsi.iloc[-1])
                st.metric("Skor RSI", f"{val:.2f}")
            else:
                st.error("Gagal ambil data. Coba lagi nanti.")

    # 5. BERITA
    elif page == "Berita Saham":
        st.title("📰 Berita")
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
            except: st.error("Berita sedang sibuk, coba beberapa saat lagi.")
