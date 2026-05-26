import streamlit as st
import yfinance as yf
import pandas as pd

# 1. Konfigurasi Halaman & Tema Putih Profesional
st.set_page_config(page_title="TradeWise AI", layout="wide")
st.markdown("""
    <style>
    .stApp { background-color: #ffffff; color: #000000; }
    h1, h2, h3, p, label { color: #000000 !important; }
    .stButton>button { background-color: #007bff !important; color: white !important; font-weight: bold; }
    .css-1544g2n { background-color: #f8f9fa !important; }
    </style>
""", unsafe_allow_html=True)

# 2. Fungsi RSI yang Aman (Mengatasi Error Series)
def calculate_rsi(data, window=14):
    delta = data['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

# 3. Sistem Login
if "authenticated" not in st.session_state: st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("🔐 Login TradeWise AI")
    pwd = st.text_input("Masukkan Password:", type="password")
    if st.button("Login"):
        if pwd == "Sefilius18":
            st.session_state.authenticated = True
            st.rerun()
        else: st.error("Password Salah!")
else:
    # 4. Navigasi Menu Samping
    st.sidebar.title("Menu Utama")
    menu = st.sidebar.radio("Navigasi:", ["Dashboard Analisis", "Tutorial RSI", "Tentang AI"])

    if menu == "Dashboard Analisis":
        st.title("📈 TradeWise AI Dashboard")
        ticker = st.text_input("Masukkan Kode Saham (Contoh: BBCA.JK atau AAPL)", "AAPL")
        
        if st.button("Dapatkan Rekomendasi"):
            with st.spinner("TradeWise AI sedang menganalisis..."):
                try:
                    df = yf.download(ticker, period="3mo", progress=False)
                    if isinstance(df, pd.DataFrame) and not df.empty and 'Close' in df.columns:
                        rsi_series = calculate_rsi(df)
                        # FIX: .iloc[-1].item() memastikan outputnya angka murni (float)
                        val = rsi_series.iloc[-1].item()
                        
                        st.line_chart(rsi_series)
                        st.metric("Skor RSI", f"{val:.2f}")
                        
                        if val < 30: st.success("🤖 AI Suggestion: OVERSOLD. Harga sedang murah, peluang beli.")
                        elif val > 70: st.warning("🤖 AI Suggestion: OVERBOUGHT. Harga terlalu mahal, sebaiknya tunggu.")
                        else: st.info("🤖 AI Suggestion: NETRAL. Tunggu sinyal konfirmasi.")
                    else: st.error("Data saham tidak ditemukan.")
                except Exception as e: st.error(f"Error teknis: {str(e)}")

    elif menu == "Tutorial RSI":
        st.title("🎓 Cara Kerja RSI")
        st.write("RSI (Relative Strength Index) adalah indikator untuk mengukur momentum harga.")
        # 
        st.write("Jika RSI di bawah 30, saham dianggap 'oversold' (murah). Jika di atas 70, saham dianggap 'overbought' (mahal).")

    elif menu == "Tentang AI":
        st.title("🤖 Tentang TradeWise AI")
        st.write("Aplikasi ini menggunakan algoritma RSI untuk membantu pemula mengambil keputusan investasi secara objektif.")

    if st.sidebar.button("Logout"):
        st.session_state.authenticated = False
        st.rerun()
