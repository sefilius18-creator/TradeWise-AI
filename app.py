import streamlit as st
import yfinance as yf
import pandas as pd
import feedparser

# ====================================
# CONFIG
# ====================================

st.set_page_config(
    page_title="TradeWise AI",
    layout="wide"
)

# ====================================
# LOGIN
# ====================================

PASSWORD = "Sefilius18"

if "login" not in st.session_state:
    st.session_state.login = False

if not st.session_state.login:

    st.title("🔐 TradeWise AI")

    pwd = st.text_input(
        "Masukkan Password",
        type="password"
    )

    if st.button("Login"):

        if pwd == PASSWORD:
            st.session_state.login = True
            st.rerun()

        else:
            st.error("Password Salah")

    st.stop()

# ====================================
# SIDEBAR
# ====================================

menu = st.sidebar.radio(
    "Menu",
    [
        "RSI",
        "Fundamental",
        "Berita"
    ]
)

# ====================================
# FUNCTION
# ====================================

@st.cache_data(ttl=3600)
@st.cache_data(ttl=3600)
def get_stock_data(ticker):

    try:

        if ".JK" not in ticker and len(ticker) == 4:
            ticker += ".JK"

        stock = yf.Ticker(ticker)

        # Ambil data harga
        df = yf.download(
            ticker,
            period="6mo",
            progress=False,
            auto_adjust=True,
            threads=False
        )

        # Ambil info fundamental
        try:
            info = stock.fast_info
        except:
            info = {}

        return df, info

    except Exception as e:

        st.error("Yahoo Finance sedang limit request. Coba lagi beberapa saat.")

        return pd.DataFrame(), {}

# ====================================
# RSI
# ====================================

if menu == "RSI":

    st.title("📈 Analisis RSI")

    ticker = st.text_input(
        "Masukkan Saham",
        "AAPL"
    )

    if st.button("Analisis"):

        df, info = get_stock_data(ticker)

        if not df.empty:

            close = df["Close"].squeeze()

            delta = close.diff()

            gain = delta.clip(lower=0)

            loss = -delta.clip(upper=0)

            avg_gain = gain.rolling(14).mean()

            avg_loss = loss.rolling(14).mean()

            rs = avg_gain / avg_loss

            rsi = 100 - (100 / (1 + rs))

            value = round(float(rsi.iloc[-1]), 2)

            st.metric("RSI", value)

            st.line_chart(rsi)

            if value < 30:
                st.success("OVERSOLD → BUY")

            elif value > 70:
                st.error("OVERBOUGHT → SELL")

            else:
                st.info("NETRAL")

# ====================================
# FUNDAMENTAL
# ====================================

elif menu == "Fundamental":

    st.title("📊 Fundamental")

    ticker = st.text_input(
        "Masukkan Saham",
        "AAPL"
    )

    if st.button("Tampilkan Fundamental"):

        df, info = get_stock_data(ticker)

        st.metric(
    "Last Price",
    info.get("lastPrice", "N/A")
)

st.metric(
    "Day High",
    info.get("dayHigh", "N/A")
)

st.metric(
    "Day Low",
    info.get("dayLow", "N/A")
)

        st.write(
            "### Nama Perusahaan"
        )

        st.write(
            info.get("longName", "N/A")
        )

# ====================================
# BERITA
# ====================================

elif menu == "Berita":

    st.title("📰 Berita Saham")

    ticker = st.text_input(
        "Masukkan Saham",
        "AAPL"
    )

    if st.button("Ambil Berita"):

        url = (
            f"https://news.google.com/rss/search?"
            f"q={ticker}+stock&hl=id&gl=ID&ceid=ID:id"
        )

        feed = feedparser.parse(url)

        if not feed.entries:

            st.warning("Berita tidak ditemukan")

        else:

            for news in feed.entries[:5]:

                st.subheader(news.title)

                st.markdown(
                    f"[Baca Berita]({news.link})"
                )

                st.divider()
