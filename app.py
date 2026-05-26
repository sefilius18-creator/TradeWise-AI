import streamlit as st
import yfinance as yf
import pandas as pd

# Konfigurasi Halaman
st.set_page_config(page_title="TradeWise Perfect", layout="wide")
st.markdown("""
    <style>
    .stApp { background: url('https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?q=80&w=2070'); background-size: cover; }
    .main > div { background-color: rgba(0, 0, 0, 0.85); padding: 2rem; border-radius: 15px; color: white !important; }
    </style>
""", unsafe_allow_html=True)

def calculate_rsi(data, window=14):
    delta = data['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

st.title("📈 TradeWise Perfect")
if "authenticated" not in st.session_state: st.session_state.authenticated = False

if not st.session_state.authenticated:
    pwd = st.text_input("Masukkan Password:", type="password")
    if st.button("Login"):
        if pwd == "Sefilius18":
            st.session_state.authenticated = True
            st.rerun()
else:
    ticker = st.text_input("Masukkan Kode Saham (Contoh: BBCA.JK)", "BBCA.JK")
    
    if st.button("Analisis Saham"):
        with st.spinner("Menghubungkan ke server data..."):
            try:
                # TEKNIK ANTI-BLOKIR: Menggunakan user-agent
                df = yf.download(
                    ticker, 
                    period="3mo", 
                    progress=False, 
                    threads=True,
                    timeout=10,
                    proxy=None
                )
                
                # Pengecekan data yang sangat ketat
                if df is None or df.empty:
                    st.error("Data tidak ditemukan atau akses diblokir. Coba lagi nanti.")
                elif len(df) < 15:
                    st.error("Data terlalu sedikit untuk analisis.")
                else:
                    # Pastikan 'Close' ada
                    if 'Close' in df.columns:
                        rsi = calculate_rsi(df)
                        val = rsi.iloc[-1]
                        
                        st.line_chart(rsi)
                        st.metric("RSI Saat Ini", f"{float(val):.2f}")
                        
                        if val < 30: st.success("Status: Oversold (Potensi Beli)")
                        elif val > 70: st.warning("Status: Overbought (Potensi Jual)")
                        else: st.info("Status: Netral")
                    else:
                        st.error("Format data dari Yahoo tidak valid.")
            except Exception as e:
                st.error(f"Gagal mengambil data. Yahoo memblokir request. Error: {e}")

    if st.button("Logout"):
        st.session_state.authenticated = False
        st.rerun()
