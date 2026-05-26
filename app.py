import streamlit as st
import yfinance as yf
import requests

# Konfigurasi Halaman (Layout Profesional)
st.set_page_config(page_title="TradeWise AI Pro", layout="wide")

# CSS untuk estetika bersih
st.markdown("""
    <style>
    .stApp { background-color: #ffffff; }
    h1, h2, h3 { color: #1e1e1e !important; }
    .stMetric { background-color: #f8f9fa; padding: 20px; border-radius: 10px; border: 1px solid #e9ecef; }
    </style>
""", unsafe_allow_html=True)

# Inisialisasi Session State Login
if "auth" not in st.session_state:
    st.session_state.auth = False

# Sistem Login
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
    # NAVIGASI GARIS 3 (Sidebar)
    with st.sidebar:
        st.header("☰ Menu Utama")
        page = st.radio("Navigasi:", ["Dashboard Analisis", "Tutorial RSI", "Fundamental & Berita"])
        st.markdown("---")
        if st.button("Logout"):
            st.session_state.auth = False
            st.rerun()

    # --- HALAMAN DASHBOARD ANALISIS ---
    if page == "Dashboard Analisis":
        st.title("📈 Dashboard Analisis")
        ticker = st.text_input("Masukkan Kode Saham (Contoh: BBCA.JK atau AAPL)", "AAPL")
        
        if st.button("Dapatkan Rekomendasi"):
            with st.spinner("TradeWise AI sedang memproses..."):
                try:
                    df = yf.download(ticker, period="3mo", progress=False)
                    if not df.empty:
                        delta = df['Close'].diff()
                        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
                        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
                        rsi = 100 - (100 / (1 + (gain / loss)))
                        
                        st.line_chart(rsi)
                        val = float(rsi.iloc[-1])
                        st.metric("Skor RSI", f"{val:.2f}")
                        
                        if val < 30: st.success("🤖 AI Suggestion: OVERSOLD (Potensi BELI)")
                        elif val > 70: st.warning("🤖 AI Suggestion: OVERBOUGHT (Potensi JUAL)")
                        else: st.info("🤖 AI Suggestion: NETRAL")
                    else: st.error("Data tidak ditemukan.")
                except Exception as e: st.error(f"Error: {e}")

    # --- HALAMAN TUTORIAL ---
    elif page == "Tutorial RSI":
        st.title("🎓 Tutorial RSI")
        st.write("Relative Strength Index (RSI) adalah indikator momentum.")
        # Gambar ilustrasi tutorial
        st.image("https://www.investopedia.com/thmb/hN83t2yNn51P2S5FhN_67S6hS8s=/1500x0/filters:no_upsert():max_bytes:150000:strip_icc()/RSI_Indicator_Example-5c0b896446e0fb000109a066.jpg")
        st.write("1. **Oversold (<30)**: Saham cenderung murah.")
        st.write("2. **Overbought (>70)**: Saham cenderung mahal.")

    # --- HALAMAN FUNDAMENTAL & BERITA ---
    elif page == "Fundamental & Berita":
        st.title("📰 Data Fundamental & Berita")
        ticker = st.text_input("Cek Fundamental & Berita Saham:", "AAPL")
        
        if st.button("Tampilkan Data"):
            with st.spinner("Mengambil data..."):
                # 1. Fundamental
                stock = yf.Ticker(ticker)
                info = stock.info
                col1, col2 = st.columns(2)
                col1.metric("P/E Ratio", info.get('trailingPE', 'N/A'))
                col2.metric("Market Cap", f"{info.get('marketCap', 0):,}")
                
                # 2. Berita Otomatis
                API_KEY = "a8f7e0c949134eea9863c652f02f8175"
                url = f"https://newsapi.org/v2/everything?q={ticker}&apiKey={API_KEY}&language=en&pageSize=3"
                
                try:
                    response = requests.get(url).json()
                    st.subheader(f"Berita Terbaru: {ticker}")
                    if response.get('articles'):
                        for article in response['articles']:
                            st.write(f"**{article['title']}**")
                            st.write(f"{article['description']}")
                            st.markdown(f"[Baca selengkapnya]({article['url']})")
                            st.divider()
                    else:
                        st.warning("Tidak ada berita ditemukan.")
                except Exception as e:
                    st.error(f"Gagal memuat berita: {e}")
