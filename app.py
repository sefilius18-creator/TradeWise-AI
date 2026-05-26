import streamlit as st
import yfinance as yf
import requests

# Konfigurasi Halaman (Wajib diletakkan paling atas)
st.set_page_config(page_title="TradeWise AI", layout="wide")

# FUNGSI CACHE (Mencegah Error Rate Limit dari Yahoo Finance)
@st.cache_data(ttl=3600)
def get_data(ticker):
    stock = yf.Ticker(ticker)
    df = stock.history(period="3mo")
    info = stock.info
    return df, info

# SISTEM LOGIN
if "auth" not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    st.title("🔐 Login TradeWise AI")
    pwd = st.text_input("Password:", type="password")
    if st.button("Login"):
        if pwd == "Sefilius18":
            st.session_state.auth = True
            st.rerun()
        else:
            st.error("Password Salah!")
else:
    # NAVIGASI SIDEBAR (GARIS 3)
    with st.sidebar:
        st.header("☰ Menu Utama")
        page = st.radio("Navigasi:", ["Dashboard Analisis", "Fundamental & Berita"])
        if st.button("Logout"):
            st.session_state.auth = False
            st.rerun()

    # DASHBOARD ANALISIS
    if page == "Dashboard Analisis":
        st.title("📈 Dashboard Analisis")
        ticker = st.text_input("Kode Saham (contoh: AAPL atau BBCA.JK):", "AAPL")
        
        if st.button("Analisis"):
            with st.spinner("TradeWise AI memproses..."):
                try:
                    df, _ = get_data(ticker)
                    if not df.empty:
                        # Rumus RSI
                        delta = df['Close'].diff()
                        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
                        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
                        rsi = 100 - (100 / (1 + (gain / loss)))
                        
                        st.line_chart(rsi)
                        val = float(rsi.iloc[-1]) # Mengambil nilai terbaru
                        st.metric("Skor RSI", f"{val:.2f}")
                        
                        if val < 30: st.success("STATUS: OVERSOLD (Potensi Beli)")
                        elif val > 70: st.error("STATUS: OVERBOUGHT (Potensi Jual)")
                        else: st.info("STATUS: NETRAL")
                    else: st.error("Data tidak ditemukan.")
                except Exception as e:
                    st.error("Gagal memuat data. Mohon tunggu 1 menit.")

    # FUNDAMENTAL & BERITA (BAHASA INDONESIA)
    elif page == "Fundamental & Berita":
        st.title("📰 Fundamental & Berita")
        ticker = st.text_input("Cek Saham:", "AAPL")
        
        if st.button("Tampilkan Berita"):
            _, info = get_data(ticker)
            st.metric("P/E Ratio", info.get('trailingPE', 'N/A'))
            
            # API Berita (language='id' untuk Bahasa Indonesia)
            API_KEY = "a8f7e0c949134eea9863c652f02f8175"
            url = f"https://newsapi.org/v2/everything?q={ticker}&apiKey={API_KEY}&language=id&pageSize=3"
            
            try:
                res = requests.get(url, timeout=10).json()
                st.subheader("Berita Terkini (Bahasa Indonesia)")
                if 'articles' in res and res['articles']:
                    for art in res['articles']:
                        st.write(f"**{art['title']}**")
                        st.write(f"{art['description']}")
                        st.markdown(f"[Baca Berita]({art['url']})")
                        st.divider()
                else:
                    st.warning("Tidak ada berita Bahasa Indonesia untuk saham ini.")
            except:
                st.error("Gagal memuat berita.")
