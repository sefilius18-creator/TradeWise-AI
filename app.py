import streamlit as st
import yfinance as yf
import pandas as pd

# 1. Konfigurasi Halaman & Tema Putih (Clean & Professional)
st.set_page_config(page_title="TradeWise AI", layout="wide")
st.markdown("""
    <style>
    /* Mengubah tema menjadi dominan putih */
    .stApp { background-color: #ffffff; color: #000000; }
    h1, h2, h3, p, label { color: #000000 !important; }
    .stButton>button { background-color: #007bff !important; color: white !important; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# 2. Fungsi RSI
def calculate_rsi(data, window=14):
    delta = data['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

# 3. Sistem Login
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("🔐 Login TradeWise AI")
    pwd = st.text_input("Masukkan Password:", type="password")
    if st.button("Login"):
        if pwd == "Sefilius18":
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("Password Salah!")
else:
    # 4. Aplikasi Utama (TradeWise AI)
    st.title("📈 TradeWise AI")
    st.write("Asisten Pintar untuk keputusan beli/jual saham Anda.")
    
    ticker = st.text_input("Masukkan Kode Saham (Contoh: BBCA.JK atau AAPL)", "AAPL")
    
    if st.button("Dapatkan Rekomendasi"):
        with st.spinner("TradeWise AI sedang menganalisis data..."):
            try:
                df = yf.download(ticker, period="3mo", progress=False)
                
                # Pengecekan data aman agar tidak error Series
                if isinstance(df, pd.DataFrame) and not df.empty and 'Close' in df.columns:
                    rsi_series = calculate_rsi(df)
                    
                    # Memastikan hanya mengambil satu nilai terakhir sebagai float
                    val = float(rsi_series.iloc[-1])
                    
                    st.line_chart(rsi_series)
                    st.metric("Skor RSI", f"{val:.2f}")
                    
                    # Rekomendasi Pro
                    if val < 30:
                        st.success("🤖 AI Suggestion: OVERSOLD. Harga sedang murah, ini kesempatan untuk BELI.")
                    elif val > 70:
                        st.warning("🤖 AI Suggestion: OVERBOUGHT. Harga terlalu mahal, sebaiknya JUAL atau TUNGGU.")
                    else:
                        st.info("🤖 AI Suggestion: NETRAL. Tunggu sinyal yang lebih kuat.")
                else:
                    st.error("Data saham tidak ditemukan. Silakan coba kode lain (Contoh: AAPL).")
            except Exception as e:
                st.error(f"Error teknis: {str(e)}")

    if st.button("Logout"):
        st.session_state.authenticated = False
        st.rerun()
