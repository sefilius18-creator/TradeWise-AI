import streamlit as st
import yfinance as yf
import pandas as pd

# Pengaturan Halaman
st.set_page_config(page_title="TradeWise", layout="wide")

# CSS untuk memastikan latar belakang gelap kembali
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: white; }
    </style>
""", unsafe_allow_html=True)

st.title("📈 Asisten Saham Pintar")

ticker = st.text_input("Masukkan Kode Saham (Contoh: BBCA.JK atau AAPL)", "AAPL")

if st.button("Dapatkan Rekomendasi"):
    with st.spinner("Mengambil data..."):
        try:
            # Menggunakan yf.download paling dasar tanpa argumen tambahan yang berisiko error
            df = yf.download(ticker, period="3mo", progress=False)
            
            # Pengecekan data yang aman agar tidak muncul error "Series is ambiguous"
            if isinstance(df, pd.DataFrame) and not df.empty and 'Close' in df.columns:
                # RSI Calculation
                delta = df['Close'].diff()
                gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
                rs = gain / loss
                rsi = 100 - (100 / (1 + rs))
                
                val = float(rsi.iloc[-1])
                
                st.line_chart(rsi)
                st.metric("Skor RSI", f"{val:.2f}")
                
                if val < 30:
                    st.success("Saran: OVERSOLD (Potensi Beli)")
                elif val > 70:
                    st.warning("Saran: OVERBOUGHT (Potensi Jual)")
                else:
                    st.info("Saran: NETRAL (Pantau terus)")
            else:
                st.error("Data tidak ditemukan. Coba lagi nanti.")
        except Exception as e:
            st.error(f"Error teknis: {e}")
