import streamlit as st
import yfinance as yf
import requests

st.set_page_config(page_title="TradeWise AI Pro", layout="wide")

# Fungsi untuk mengambil data saham dengan Cache agar tidak kena limit
@st.cache_data(ttl=3600)
def fetch_stock_data(ticker):
    stock = yf.Ticker(ticker)
    df = stock.history(period="3mo")
    return df, stock.info

# Sistem Login
if "auth" not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    st.title("🔐 Login TradeWise AI")
    pwd = st.text_input("Password:", type="password")
    if st.button("Login"):
        if pwd == "Sefilius18": st.session_state.auth = True; st.rerun()
        else: st.error("Password Salah!")
else:
    # Sidebar Menu
    with st.sidebar:
        st.header("☰ Menu Utama")
        page = st.radio("Navigasi:", ["Dashboard Analisis", "Tutorial RSI", "Fundamental & Berita"])
        if st.button("Logout"): st.session_state.auth = False; st.rerun()

    # --- DASHBOARD ---
    if page == "Dashboard Analisis":
        st.title("📈 Dashboard Analisis")
        ticker = st.text_input("Kode Saham (Contoh: AAPL atau BBCA.JK)", "AAPL")
        if st.button("Analisis"):
            try:
                df, _ = fetch_stock_data(ticker)
                if not df.empty:
                    delta = df['Close'].diff()
                    gain = (delta.where(delta > 0, 0)).rolling(14).mean()
                    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
                    rsi = 100 - (100 / (1 + (gain / loss)))
                    
                    st.line_chart(rsi)
                    val = float(rsi.iloc[-1]) # Mengambil nilai terbaru sebagai angka
                    st.metric("Skor RSI", f"{val:.2f}")
                    
                    if val < 30: st.success("OVERSOLD: Potensi Beli")
                    elif val > 70: st.error("OVERBOUGHT: Potensi Jual")
                    else: st.info("NETRAL")
                else: st.error("Saham tidak ditemukan.")
            except Exception as e: st.error(f"Error: {e}")

    # --- FUNDAMENTAL & BERITA ---
    elif page == "Fundamental & Berita":
        st.title("📰 Data & Berita")
        ticker = st.text_input("Cek Saham:", "AAPL")
        if st.button("Tampilkan Berita"):
            _, info = fetch_stock_data(ticker)
            st.metric("P/E Ratio", info.get('trailingPE', 'N/A'))
            
            # Integrasi NewsAPI
            API_KEY = "a8f7e0c949134eea9863c652f02f8175"
            url = f"https://newsapi.org/v2/everything?q={ticker}&apiKey={API_KEY}&language=en&pageSize=3"
            try:
                res = requests.get(url).json()
                if 'articles' in res:
                    for article in res['articles']:
                        st.write(f"**{article['title']}**")
                        st.markdown(f"[Baca]({article['url']})")
                else: st.warning("Berita tidak tersedia.")
            except: st.error("Gagal memuat berita.")
