import streamlit as st
import yfinance as yf
import pandas as pd

# Konfigurasi Halaman Profesional
st.set_page_config(page_title="TradeWise AI Pro", layout="wide")

# CSS untuk estetika bersih
st.markdown("""
    <style>
    .stApp { background-color: #ffffff; }
    h1, h2, h3 { color: #1e1e1e !important; }
    .stMetric { background-color: #f8f9fa; padding: 20px; border-radius: 10px; border: 1px solid #e9ecef; }
    .suggestion-box { padding: 15px; border-radius: 10px; margin-bottom: 20px; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# Fungsi RSI dengan penanganan error
def get_rsi_analysis(ticker):
    df = yf.download(ticker, period="3mo", progress=False)
    if df.empty or 'Close' not in df.columns: return None, None
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
    rsi = 100 - (100 / (1 + (gain / loss)))
    return rsi, rsi.iloc[-1].item()

# Sistem Login
if "auth" not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    st.title("🔐 TradeWise AI Login")
    pwd = st.text_input("Password:", type="password")
    if st.button("Login"):
        if pwd == "Sefilius18": st.session_state.auth = True; st.rerun()
else:
    with st.sidebar:
        st.header("☰ Menu Utama")
        page = st.radio("Navigasi:", ["Dashboard Analisis", "Tutorial RSI", "Fundamental & Berita"])
        if st.button("Logout"): st.session_state.auth = False; st.rerun()

    # --- DASHBOARD ANALISIS ---
    if page == "Dashboard Analisis":
        st.title("📈 Dashboard Analisis")
        ticker = st.text_input("Masukkan Kode Saham (Contoh: BBCA.JK)", "AAPL")
        
        if st.button("Jalankan Analisis"):
            with st.spinner("Menganalisis..."):
                rsi_series, val = get_rsi_analysis(ticker)
                if rsi_series is not None:
                    st.line_chart(rsi_series)
                    st.metric("Skor RSI", f"{val:.2f}")
                    
                    # Logika detail RSI
                    st.subheader("🤖 Analisis AI")
                    if val < 30:
                        st.success("STATUS: OVERSOLD (Jenuh Jual). Harga dianggap murah, potensi pembalikan arah ke atas (Buy Zone).")
                    elif val > 70:
                        st.error("STATUS: OVERBOUGHT (Jenuh Beli). Harga dianggap terlalu mahal, waspada potensi koreksi/penurunan (Sell Zone).")
                    elif 50 < val <= 70:
                        st.warning("STATUS: BULLISH. Tren sedang menguat, namun belum jenuh beli. Pertahankan posisi.")
                    elif 30 <= val <= 50:
                        st.info("STATUS: BEARISH. Tren sedang melemah, namun belum jenuh jual. Tunggu konfirmasi.")
                    else:
                        st.write("Status Netral.")
                else: st.error("Data tidak ditemukan.")

    # --- TUTORIAL RSI ---
    elif page == "Tutorial RSI":
        st.title("🎓 Memahami RSI")
        st.write("""
        Relative Strength Index (RSI) adalah indikator momentum yang mengukur kecepatan dan perubahan pergerakan harga.
        * **Skor 0-30**: Menandakan aset *Oversold*. Sering dianggap sebagai sinyal beli karena harga sudah terlalu rendah.
        * **Skor 70-100**: Menandakan aset *Overbought*. Sering dianggap sebagai sinyal jual karena harga sudah terlalu tinggi.
        * **Skor 50**: Batas tengah yang menentukan dominasi pembeli atau penjual.
        """)

    # --- FUNDAMENTAL & BERITA ---
    elif page == "Fundamental & Berita":
        st.title("📰 Data & Fundamental")
        st.info("Catatan: Data fundamental real-time memerlukan API berbayar. Saat ini, kami menyediakan ringkasan teknikal.")
        st.write("Untuk fundamental, selalu cek: **PER (Price to Earnings Ratio)**, **PBV (Price to Book Value)**, dan **Dividen Yield** melalui laporan keuangan perusahaan.")
        st.write("---")
        st.subheader("Berita Saham")
        st.write("Gunakan fitur ini untuk memantau sentimen pasar. Fokus pada berita mengenai laba kuartalan dan kebijakan suku bunga.")
