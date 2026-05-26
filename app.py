import streamlit as st
import yfinance as yf
import pandas as pd

# 1. Konfigurasi Halaman & CSS Background Grafik
st.set_page_config(page_title="TradeWise Perfect", layout="wide")
st.markdown("""
    <style>
    .stApp { 
        background: url('https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?q=80&w=2070'); 
        background-size: cover; 
    }
    .main > div { 
        background-color: rgba(0, 0, 0, 0.85); 
        padding: 2rem; 
        border-radius: 15px; 
        color: white !important; 
    }
    </style>
""", unsafe_allow_html=True)

# 2. Fungsi RSI yang sudah diperbaiki agar tidak error 'Series'
def calculate_rsi(data, window=14):
    delta = data['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

# 3. Aplikasi Utama
st.title("📈 Asisten Saham Pintar")

ticker = st.text_input("Masukkan Kode Saham (Contoh: BBCA.JK atau AAPL)", "AAPL")

if st.button("Dapatkan Rekomendasi"):
    with st.spinner("Menganalisis data..."):
        try:
            # Menggunakan yf.download paling standar
            df = yf.download(ticker, period="3mo", progress=False)
            
            # Pengecekan data yang aman (Strict Check)
            if isinstance(df, pd.DataFrame) and not df.empty and 'Close' in df.columns:
                rsi_series = calculate_rsi(df)
                
                # Mengambil nilai terakhir dengan aman sebagai angka (float)
                # Ini menghindari error 'float() argument must be... not Series'
                val = float(rsi_series.iloc[-1])
                
                st.line_chart(rsi_series)
                st.metric("Skor RSI Saat Ini", f"{val:.2f}")
                
                # Logika Rekomendasi Pro untuk Pemula
                if val < 30:
                    st.success("Saran: OVERSOLD (Potensi Beli - Harga Murah)")
                elif val > 70:
                    st.warning("Saran: OVERBOUGHT (Potensi Jual - Harga Mahal)")
                else:
                    st.info("Saran: NETRAL (Pantau Terus)")
            else:
                st.error("Data gagal dimuat. Pastikan kode saham benar dan server tidak sedang memblokir akses.")
        except Exception as e:
            st.error(f"Error teknis: {str(e)}")
