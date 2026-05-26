import streamlit as st
import yfinance as yf
import requests
import pandas as pd

st.set_page_config(page_title="TradeWise AI Pro", layout="wide")

@st.cache_data(ttl=3600)
def get_data(ticker):
    try:
        df = yf.download(ticker, period="6mo", progress=False)
        info = yf.Ticker(ticker).info
        return df, info
    except: return pd.DataFrame(), {}

# Sistem Navigasi
page = st.sidebar.radio("Menu:", ["Analisis Teknikal", "Fundamental & Berita"])

if page == "Analisis Teknikal":
    st.title("📈 Analisis Teknikal & Rekomendasi")
    ticker = st.text_input("Kode Saham (Contoh: AAPL):", "AAPL")
    if st.button("Analisis RSI"):
        df, _ = get_data(ticker)
        if not df.empty:
            delta = df['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
            rsi = 100 - (100 / (1 + (gain / loss)))
            val = float(rsi.iloc[-1])
            
            st.line_chart(rsi)
            st.metric("Skor RSI", f"{val:.2f}")
            
            # LOGIKA REKOMENDASI CERDAS
            if val < 30:
                st.success("STATUS: OVERSOLD (Jenuh Jual). Rekomendasi: **PELUANG BELI**")
            elif val > 70:
                st.error("STATUS: OVERBOUGHT (Jenuh Beli). Rekomendasi: **PELUANG JUAL / TUNGGU KOREKSI**")
            else:
                st.info("STATUS: NETRAL. Rekomendasi: **WAIT AND SEE**")
        else: st.warning("Data tidak tersedia.")

elif page == "Fundamental & Berita":
    st.title("📰 Fundamental & Berita")
    ticker = st.text_input("Cek Saham:", "AAPL")
    if st.button("Analisis Fundamental"):
        _, info = get_data(ticker)
        
        # Fundamental Data
        col1, col2 = st.columns(2)
        with col1: st.metric("P/E Ratio", info.get('trailingPE', 'N/A'))
        with col2: st.metric("Market Cap", f"{info.get('marketCap', 0)/1e9:.2f} B")
        
        # Berita Terkini
        st.subheader("Berita Utama:")
        API_KEY = "a8f7e0c949134eea9863c652f02f8175"
        url = f"https://newsapi.org/v2/everything?q={ticker}&apiKey={API_KEY}&language=id&pageSize=3"
        try:
            res = requests.get(url, timeout=10).json()
            for art in res.get('articles', []):
                st.write(f"### {art['title']}")
                st.write(art['description'])
                st.markdown(f"[Baca Sumber Asli]({art['url']})")
                st.divider()
        except: st.error("Berita gagal dimuat.")
