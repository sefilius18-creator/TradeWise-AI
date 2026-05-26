import streamlit as st
import yfinance as yf
import requests

# 1. Konfigurasi Halaman (Wajib di baris paling atas)
st.set_page_config(page_title="TradeWise AI", layout="wide")

# 2. Inisialisasi Session
if "auth" not in st.session_state: st.session_state.auth = False

# 3. Fungsi Data (Cache agar tidak terkena limit)
@st.cache_data(ttl=3600)
def get_data(ticker):
    stock = yf.Ticker(ticker)
    df = stock.history(period="3mo")
    return df, stock.info

# 4. SISTEM LOGIN
if not st.session_state.auth:
    st.title("🔐 TradeWise AI Login")
    pwd = st.text_input("Password:", type="password")
    if st.button("Login"):
        if pwd == "Sefilius18": st.session_state.auth = True; st.rerun()
        else: st.error("Password Salah!")
else:
    # 5. SIDEBAR (GARIS 3 OTOMATIS)
    with st.sidebar:
        st.header("☰ Menu Utama")
        page = st.radio("Navigasi:", ["Dashboard Analisis", "Tutorial RSI", "Fundamental & Berita"])
        if st.button("Logout"): st.session_state.auth = False; st.rerun()

    # 6. DASHBOARD ANALISIS
    if page == "Dashboard Analisis":
        st.title("📈 Dashboard Analisis")
        ticker = st.text_input("Kode Saham (Contoh: AAPL):", "AAPL")
        if st.button("Analisis"):
            with st.spinner("Memproses..."):
                df, _ = get_data(ticker)
                if not df.empty:
                    delta = df['Close'].diff()
                    gain = (delta.where(delta > 0, 0)).rolling(14).mean()
                    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
                    rsi = 100 - (100 / (1 + (gain / loss)))
                    st.line_chart(rsi)
                    val = float(rsi.iloc[-1])
                    st.metric("Skor RSI", f"{val:.2f}")
                    if val < 30: st.success("STATUS: OVERSOLD (Beli)")
                    elif val > 70: st.error("STATUS: OVERBOUGHT (Jual)")
                    else: st.info("STATUS: NETRAL")
                else: st.error("Data tidak ditemukan.")

    # 7. TUTORIAL
    elif page == "Tutorial RSI":
        st.title("🎓 Tutorial RSI")
        st.write("RSI adalah indikator untuk melihat kejenuhan harga.")
        [attachment_0](attachment)

    # 8. FUNDAMENTAL & BERITA
    elif page == "Fundamental & Berita":
        st.title("📰 Data Fundamental & Berita")
        ticker = st.text_input("Cek Saham:", "AAPL")
        if st.button("Tampilkan"):
            _, info = get_data(ticker)
            st.metric("P/E Ratio", info.get('trailingPE', 'N/A'))
            
            # Integrasi API Berita
            API_KEY = "a8f7e0c949134eea9863c652f02f8175"
            url = f"https://newsapi.org/v2/everything?q={ticker}&apiKey={API_KEY}&pageSize=3"
            try:
                res = requests.get(url).json()
                for art in res.get('articles', []):
                    st.write(f"**{art['title']}**")
                    st.markdown(f"[Baca]({art['url']})")
                    st.divider()
            except: st.error("Berita gagal dimuat.")
