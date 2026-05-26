import streamlit as st
import yfinance as yf
import pandas as pd

# 1. Konfigurasi Halaman & CSS untuk Kontras Maksimal
st.set_page_config(page_title="TradeWise Perfect", layout="wide", page_icon="📈")
st.markdown("""
    <style>
    .stApp { background: url('https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?q=80&w=2070'); background-size: cover; }
    .main > div { 
        background-color: rgba(0, 0, 0, 0.85); 
        padding: 2rem; 
        border-radius: 15px; 
        color: white !important; 
    }
    h1, h2, h3, .stMarkdown, .stMetric { color: #ffffff !important; }
    .stButton>button { width: 100%; background-color: #38bdf8 !important; color: black !important; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# 2. Fungsi RSI yang Aman (Robust)
def calculate_rsi(data, window=14):
    delta = data['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

# 3. Sistem Login Sederhana
st.title("📈 TradeWise Perfect")
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    pwd = st.text_input("Masukkan Password:", type="password")
    if st.button("Login"):
        if pwd == "Sefilius18":
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("Password Salah!")
else:
    # 4. Aplikasi Utama
    ticker = st.text_input("Masukkan Kode Saham (Contoh: BBCA.JK)", "BBCA.JK")
    
    if st.button("Analisis Saham"):
        # Gunakan blok try-except agar aplikasi tidak pernah crash
        try:
            df = yf.download(ticker, period="3mo", progress=False)
            
            # CEK KONDISI DATA YANG AMAN (Menghindari Error Ambiguous)
            if df is not None and not df.empty and 'Close' in df.columns and len(df) > 14:
                rsi = calculate_rsi(df)
                val = rsi.iloc[-1]
                
                # Cek apakah nilai valid (bukan NaN)
                if pd.notnull(val):
                    st.line_chart(rsi)
                    st.metric("RSI Saat Ini", f"{float(val):.2f}")
                    
                    if val < 30: 
                        st.success("Status: Oversold (Potensi Beli)")
                    elif val > 70: 
                        st.warning("Status: Overbought (Potensi Jual)")
                    else: 
                        st.info("Status: Netral")
                else:
                    st.error("Data RSI tidak valid (Saham tidak likuid).")
            else:
                st.error("Data tidak ditemukan. Pastikan ticker benar dan akhiran .JK (Contoh: BBCA.JK).")
        except Exception as e:
            st.error(f"Sistem sedang sibuk, silakan coba lagi.")
            
    if st.button("Logout"):
        st.session_state.authenticated = False
        st.rerun()
