import streamlit as st
import yfinance as yf
import requests

# Konfigurasi Halaman agar tampil profesional
st.set_page_config(page_title="TradeWise AI Pro", layout="wide")

# CSS untuk estetika bersih
st.markdown("""
    <style>
    .stApp { background-color: #ffffff; }
    </style>
""", unsafe_allow_html=True)

# 1. FUNGSI AMBIL DATA (Menggunakan Caching untuk cegah Error Rate Limit)
@st.cache_data(ttl=3600)
def fetch_stock_data(ticker):
    stock = yf.Ticker(ticker)
    df = stock.history(period="3mo")
    return df, stock.info

# 2. SISTEM LOGIN
if "auth" not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    st.title("🔐 Login TradeWise AI")
    pwd = st.text_input("Masukkan Password:", type="password")
    if st.button("Login"):
        if pwd == "Sefilius18":
            st.session_state.auth = True
            st.rerun()
        else:
            st.error("Password Salah!")
else:
    # Sidebar Navigasi
    with st.sidebar:
        st.header("☰ Menu Utama")
        page = st.radio("Navigasi:", ["Dashboard Analisis", "Tutorial RSI", "Fundamental & Berita"])
        if st.button("Logout"):
            st.session_state.auth = False
            st.rerun()

    # --- DASHBOARD ANALISIS ---
    if page == "Dashboard Analisis":
        st.title("📈 Dashboard Analisis")
        ticker = st.text_input("Kode Saham (Contoh: AAPL atau BBCA.JK)", "AAPL")
        
        if st.button("Dapatkan Rekomendasi"):
            with st.spinner("TradeWise AI memproses data..."):
                try:
                    df, _ = fetch_stock_data(ticker)
                    if not df.empty:
                        # Perhitungan RSI
                        delta = df['Close'].diff()
                        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
                        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
                        rsi = 100 - (100 / (1 + (gain / loss)))
                        
                        st.line_chart(rsi)
                        
                        # Fix Error Series: Menggunakan .iloc[-1] untuk ambil nilai terbaru
                        val = float(rsi.iloc[-1])
                        st.metric("Skor RSI Saat Ini", f"{val:.2f}")
                        
                        if val < 30: st.success("🤖 AI Suggestion: OVERSOLD (Potensi BELI)")
                        elif val > 70: st.warning("🤖 AI Suggestion: OVERBOUGHT (Potensi JUAL)")
                        else: st.info("🤖 AI Suggestion: NETRAL")
                    else: st.error("Saham tidak ditemukan.")
                except Exception as e: st.error(f"Error: {e}")

    # --- TUTORIAL RSI ---
    elif page == "Tutorial RSI":
        st.title("🎓 Tutorial RSI")
        st.write("Relative Strength Index (RSI) adalah indikator momentum untuk mengukur kecepatan perubahan harga.")
        # [attachment_0](attachment)

    # --- FUNDAMENTAL & BERITA ---
    elif page == "Fundamental & Berita":
        st.title("📰 Data Fundamental & Berita")
        ticker = st.text_input("Cek Saham:", "AAPL")
        
        if st.button("Tampilkan Berita"):
            _, info = fetch_stock_data(ticker)
            st.subheader(f"Data Fundamental: {ticker}")
            st.metric("P/E Ratio", info.get('trailingPE', 'N/A'))
            
            # Integrasi Berita dengan API Key Anda
            API_KEY = "a8f7e0c949134eea9863c652f02f8175"
            url = f"https://newsapi.org/v2/everything?q={ticker}&apiKey={API_KEY}&language=en&pageSize=3"
            
            try:
                res = requests.get(url).json()
                st.subheader("Berita Pasar Terkini")
                if 'articles' in res and res['articles']:
                    for art in res['articles']:
                        st.write(f"**{art['title']}**")
                        st.markdown(f"[Baca Berita]({art['url']})")
                        st.divider()
                else: st.warning("Tidak ada berita ditemukan.")
            except Exception as e: st.error(f"Gagal memuat berita: {e}")
