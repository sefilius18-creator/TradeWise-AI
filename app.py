import streamlit as st
import yfinance as yf
import pandas as pd

# Konfigurasi Halaman
st.set_page_config(page_title="TradeWise Pro", layout="wide")

# Fungsi RSI
def calculate_rsi(data, window=14):
    delta = data['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

# --- SISTEM LOGIN ---
if "authenticated" not in st.session_state: st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("🔐 Login TradeWise Pro")
    pwd = st.text_input("Masukkan Password:", type="password")
    if st.button("Login"):
        if pwd == "Sefilius18":
            st.session_state.authenticated = True
            st.rerun()
        else: st.error("Password Salah!")
else:
    # --- NAVIGASI MENU ---
    st.sidebar.title("Navigasi TradeWise")
    menu = st.sidebar.radio("Pilih Fitur:", ["Dashboard Analisis", "Cara Membaca Saham", "Logout"])

    if menu == "Dashboard Analisis":
        st.title("📈 Asisten Saham Pintar")
        ticker = st.text_input("Masukkan Kode Saham (Contoh: BBCA.JK)", "BBCA.JK")
        
        if st.button("Dapatkan Rekomendasi"):
            with st.spinner("Menganalisis pola saham untuk Anda..."):
                try:
                    df = yf.download(ticker, period="3mo", progress=False)
                    if not df.empty and 'Close' in df.columns:
                        rsi_series = calculate_rsi(df)
                        rsi = float(rsi_series.iloc[-1])
                        
                        st.line_chart(rsi_series)
                        st.metric("Skor RSI", f"{rsi:.2f}")
                        
                        # LOGIKA REKOMENDASI UNTUK PEMULA
                        st.subheader("💡 Saran Trader Pro:")
                        if rsi < 30:
                            st.success(f"**BELI SEKARANG!** {ticker} sedang dalam posisi 'Oversold' (Harga murah). Ini kesempatan bagus untuk masuk.")
                        elif rsi > 70:
                            st.warning(f"**JANGAN BELI!** {ticker} sudah 'Overbought' (Harga sudah terlalu tinggi). Tunggu harga turun.")
                        else:
                            st.info(f"**TUNGGU DULU.** {ticker} masih bergerak stabil. Pantau terus sampai ada sinyal beli atau jual.")
                    else:
                        st.error("Data tidak ditemukan. Pastikan ticker benar.")
                except Exception as e:
                    st.error("Error teknis, coba lagi nanti.")

    elif menu == "Cara Membaca Saham":
        st.title("🎓 Panduan Cepat Pemula")
        st.write("""
        * **RSI < 30**: Harga saham dianggap murah (Oversold). Biasanya ini waktu yang tepat untuk **Beli**.
        * **RSI > 70**: Harga saham dianggap terlalu mahal (Overbought). Biasanya ini waktu yang tepat untuk **Jual** atau **Tunggu**.
        * **Netral**: Jika RSI di antara 30-70, saham sedang dalam kondisi normal.
        """)
        
    elif menu == "Logout":
        st.session_state.authenticated = False
        st.rerun()
