import streamlit as st
import yfinance as yf
import pandas as pd

# Layout Lebar
st.set_page_config(page_title="TradeWise AI Pro", layout="wide")

# CSS Profesional
st.markdown("""
    <style>
    .stApp { background-color: #f8f9fa; }
    .stMetric { background-color: white; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
    </style>
""", unsafe_allow_html=True)

# Login
if "auth" not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    pwd = st.text_input("Password:", type="password")
    if st.button("Login"):
        if pwd == "Sefilius18": st.session_state.auth = True; st.rerun()
else:
    # Header & Ticker
    st.title("📊 TradeWise AI - Command Center")
    ticker = st.text_input("Cari Saham (Contoh: BBCA.JK)", "AAPL")
    
    # --- DASHBOARD TATA LETAK KOLOM (Agar Tidak Cuman 1 Menu) ---
    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("Visualisasi & Sinyal")
        if st.button("Jalankan Analisis Pro"):
            df = yf.download(ticker, period="3mo", progress=False)
            if not df.empty:
                # RSI
                delta = df['Close'].diff()
                gain = (delta.where(delta > 0, 0)).rolling(14).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
                rsi = 100 - (100 / (1 + (gain / loss)))
                
                st.line_chart(rsi)
                val = rsi.iloc[-1].item()
                st.metric("RSI Terbaru", f"{val:.2f}")
            else: st.error("Data tidak ditemukan.")

    with col2:
        st.subheader("Ringkasan Cepat")
        st.info("💡 **Tips Trader:**")
        st.write("- RSI < 30 = Oversold (Murah)")
        st.write("- RSI > 70 = Overbought (Mahal)")
        st.write("- Selalu cek volume transaksi!")
        
        st.subheader("Berita Pasar")
        st.write("Fitur Live Feed akan segera terintegrasi secara otomatis.")

    if st.button("Logout"): st.session_state.auth = False; st.rerun()
