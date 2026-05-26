import streamlit as st
import yfinance as yf
import requests
import pandas as pd

st.set_page_config(page_title="TradeWise AI Pro", layout="wide")

# 1. CACHE DATA AGAR TIDAK DIBLOKIR YAHOO FINANCE
# ttl=86400 (cache disimpan selama 24 jam)
@st.cache_data(ttl=86400)
def get_safe_data(ticker):
    try:
        # Menggunakan yf.download lebih stabil & ringan
        df = yf.download(ticker, period="3mo", progress=False)
        return df
    except Exception:
        return pd.DataFrame()

# 2. SISTEM LOGIN
if "auth" not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    st.title("🔐 TradeWise AI Login")
    pwd = st.text_input("Password:", type="password")
    if st.button("Login"):
        if pwd == "Sefilius18": st.session_state.auth = True; st.rerun()
        else: st.error("Password Salah!")
else:
    # 3. SIDEBAR NAVIGASI
    with st.sidebar:
        st.header("☰ Menu Utama")
        page = st.radio("Navigasi:", ["Dashboard Analisis", "Berita Saham"])
        if st.button("Logout"): st.session_state.auth = False; st.rerun()

    # 4. DASHBOARD ANALISIS (RSI)
    if page == "Dashboard Analisis":
        st.title("📈 Analisis RSI")
        ticker = st.text_input("Kode Saham (Contoh: AAPL atau BBCA.JK):", "AAPL")
        
        if st.button("Analisis"):
            with st.spinner("Memproses data..."):
                df = get_safe_data(ticker)
                if not df.empty and 'Close' in df.columns:
                    # Perhitungan RSI
                    close = df['Close']
                    delta = close.diff()
                    gain = (delta.where(delta > 0, 0)).rolling(14).mean()
                    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
                    rsi = 100 - (100 / (1 + (gain / loss)))
                    
                    st.line_chart(rsi)
                    
                    # FIX: Ambil nilai terakhir dengan .iloc[-1] agar tidak error Series
                    val = float(rsi.iloc[-1])
                    st.metric("Skor RSI", f"{val:.2f}")
                    
                    if val < 30: st.success("STATUS: OVERSOLD (Potensi Beli)")
                    elif val > 70: st.error("STATUS: OVERBOUGHT (Potensi Jual)")
                    else: st.info("STATUS: NETRAL")
                else:
                    st.warning("Data tidak tersedia/server sibuk. Harap tunggu beberapa saat.")

    # 5. BERITA SAHAM
    elif page == "Berita Saham":
        st.title("📰 Berita Saham")
        ticker = st.text_input("Cari berita:", "AAPL")
        if st.button("Tampilkan Berita"):
            API_KEY = "a8f7e0c949134eea9863c652f02f8175"
            url = f"https://newsapi.org/v2/everything?q={ticker}&apiKey={API_KEY}&language=id&pageSize=3"
            try:
                res = requests.get(url, timeout=10).json()
                articles = res.get('articles', [])
                if articles:
                    for art in articles:
                        st.write(f"**{art['title']}**")
                        st.markdown(f"[Baca Berita]({art['url']})")
                        st.divider()
                else:
                    st.warning("Tidak ada berita Bahasa Indonesia ditemukan.")
            except:
                st.error("Gagal memuat berita. Periksa koneksi.")
