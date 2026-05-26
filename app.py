import streamlit as st
import yfinance as yf
import pandas as pd

# Konfigurasi Halaman (Layout Profesional)
st.set_page_config(page_title="TradeWise AI", layout="wide", page_icon="📈")

# CSS untuk tema bersih (White Theme)
st.markdown("""
    <style>
    .stApp { background-color: #ffffff; color: #000000; }
    .css-1d391kg { background-color: #f0f2f6; } /* Sidebar color */
    h1, h2, h3, p, label { color: #000000 !important; }
    .stButton>button { border-radius: 5px; background-color: #007bff; color: white; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# Fungsi RSI (Anti-Error)
def calculate_rsi(data, window=14):
    delta = data['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

# Sistem Login
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
    # NAVIGASI GARIS 3 (Otomatis muncul di sidebar Streamlit)
    with st.sidebar:
        st.header("☰ Menu Utama")
        menu = st.radio("Navigasi:", ["Dashboard Analisis", "Tutorial RSI", "Tentang AI"])
        st.markdown("---")
        if st.button("Logout"):
            st.session_state.authenticated = False
            st.rerun()

    # Konten Menu
    if menu == "Dashboard Analisis":
        st.title("📈 Dashboard Analisis")
        ticker = st.text_input("Masukkan Kode Saham (Contoh: BBCA.JK)", "AAPL")
        
        if st.button("Analisis Saham"):
            with st.spinner("TradeWise AI sedang memproses data..."):
                try:
                    df = yf.download(ticker, period="3mo", progress=False)
                    if not df.empty and 'Close' in df.columns:
                        rsi_series = calculate_rsi(df)
                        # Menggunakan .item() agar tidak error 'Series'
                        val = rsi_series.iloc[-1].item()
                        
                        st.line_chart(rsi_series)
                        st.metric("Skor RSI", f"{val:.2f}")
                        
                        if val < 30: st.success("🤖 AI Suggestion: OVERSOLD (Potensi BELI)")
                        elif val > 70: st.warning("🤖 AI Suggestion: OVERBOUGHT (Potensi JUAL)")
                        else: st.info("🤖 AI Suggestion: NETRAL")
                    else: st.error("Data tidak ditemukan.")
                except Exception as e: st.error(f"Error: {e}")

    elif menu == "Tutorial RSI":
        st.title("🎓 Tutorial RSI")
        st.write("Relative Strength Index (RSI) adalah indikator momentum.")
        [attachment_0](attachment)
        st.write("1. **Oversold (<30)**: Saham cenderung murah, potensi *rebound*.")
        st.write("2. **Overbought (>70)**: Saham cenderung mahal, potensi koreksi.")

    elif menu == "Tentang AI":
        st.title("🤖 Tentang TradeWise AI")
        st.write("Aplikasi ini dibuat untuk membantu trader pemula mengambil keputusan berbasis data secara objektif.")
