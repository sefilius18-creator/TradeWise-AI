import streamlit as st
import yfinance as yf
import pandas as pd

# Konfigurasi Halaman
st.set_page_config(page_title="TradeWise AI Pro", layout="wide")

# CSS Profesional untuk tampilan bersih
st.markdown("""
    <style>
    .stApp { background-color: #ffffff; }
    h1, h2, h3 { color: #1e1e1e !important; }
    .stMetric { background-color: #f8f9fa; padding: 20px; border-radius: 10px; border: 1px solid #e9ecef; }
    </style>
""", unsafe_allow_html=True)

# Login System
if "auth" not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    st.title("🔐 TradeWise AI Login")
    pwd = st.text_input("Password:", type="password")
    if st.button("Login"):
        if pwd == "Sefilius18": st.session_state.auth = True; st.rerun()
else:
    # Sidebar Navigation (Menu Garis 3)
    with st.sidebar:
        st.header("☰ Menu Utama")
        page = st.radio("Navigasi:", ["Dashboard Analisis", "Fundamental & Berita", "Tutorial"])
        st.markdown("---")
        if st.button("Logout"): st.session_state.auth = False; st.rerun()

    # --- KONTEN PROFESIONAL ---
    if page == "Dashboard Analisis":
        st.title("📈 Dashboard Analisis")
        ticker = st.text_input("Masukkan Kode Saham (Contoh: AAPL)", "AAPL")
        
        if st.button("Analisis"):
            with st.spinner("Memuat data..."):
                df = yf.download(ticker, period="3mo", progress=False)
                if not df.empty:
                    # RSI Calculation
                    delta = df['Close'].diff()
                    gain = (delta.where(delta > 0, 0)).rolling(14).mean()
                    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
                    rsi = 100 - (100 / (1 + (gain / loss)))
                    
                    st.line_chart(rsi)
                    val = rsi.iloc[-1].item()
                    st.metric("RSI Saat Ini", f"{val:.2f}")
                else: st.error("Saham tidak ditemukan.")

    elif page == "Fundamental & Berita":
        st.title("📰 Data & Fundamental")
        st.subheader("Ringkasan Fundamental")
        st.write("Data fundamental akan tampil di sini untuk membantu Anda menilai kesehatan perusahaan.")
        st.subheader("Berita Saham Terkini")
        st.info("Fitur *Live Feed* sedang dalam tahap optimasi agar tidak membebani kecepatan *loading* aplikasi.")

    elif page == "Tutorial":
        st.title("🎓 Panduan Investasi")
        st.write("Pelajari cara menggunakan RSI dan indikator lain untuk memaksimalkan profit Anda.")
