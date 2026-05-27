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

@st.cache_data(ttl=300)
def get_stock_data(ticker):

    try:

        ticker = ticker.upper().strip()

        # Tambahkan .JK hanya saham Indonesia
        if len(ticker) == 4 and "." not in ticker:
            ticker += ".JK"

        # Download data
        df = yf.download(
            tickers=ticker,
            period="3mo",
            interval="1d",
            auto_adjust=True,
            progress=False,
            threads=False
        )

        # Pastikan dataframe valid
        if df is None or df.empty:
            return pd.DataFrame(), {}

        # Ambil fundamental ringan
        try:

            stock = yf.Ticker(ticker)

            fast = stock.fast_info

            info = {
                "lastPrice": fast.get("lastPrice"),
                "dayHigh": fast.get("dayHigh"),
                "dayLow": fast.get("dayLow")
            }

        except:

            info = {}

        return df, info

    except Exception as e:

        st.error(f"Error: {e}")

        return pd.DataFrame(), {}

# ====================================
# RSI
# ====================================

if menu == "RSI":

    st.title("📈 Analisis RSI")

    market = st.selectbox(
        "Pilih Market",
        ["US", "Indonesia"]
    )

    ticker = st.text_input(
        "Masukkan Saham",
        "AAPL"
    )

    if st.button("Analisis"):

        with st.spinner("Mengambil data saham..."):

            # Format ticker
            if market == "Indonesia":
                ticker_final = ticker.upper() + ".JK"
            else:
                ticker_final = ticker.upper()

            # Ambil data
            df, info = get_stock_data(ticker_final)

        st.write("Ticker:", ticker_final)
        st.write("Jumlah Data:", len(df))

        if df.empty:

            st.error("Data saham tidak ditemukan")

        else:

            try:

                close = df["Close"]

                if isinstance(close, pd.DataFrame):
                    close = close.iloc[:, 0]

                delta = close.diff()

                gain = delta.clip(lower=0)

                loss = -delta.clip(upper=0)

                avg_gain = gain.rolling(14).mean()

                avg_loss = loss.rolling(14).mean()

                rs = avg_gain / avg_loss

                rsi = 100 - (100 / (1 + rs))

                latest_rsi = float(rsi.iloc[-1])

                latest_price = float(close.iloc[-1])

                st.metric(
                    "Harga Saat Ini",
                    round(latest_price, 2)
                )

                st.metric(
                    "RSI",
                    round(latest_rsi, 2)
                )

                st.line_chart(rsi)

                if latest_rsi < 30:

                    st.success(
                        "OVERSOLD → Potensi BUY"
                    )

                elif latest_rsi > 70:

                    st.error(
                        "OVERBOUGHT → Potensi SELL"
                    )

                else:

                    st.info(
                        "NETRAL → WAIT & SEE"
                    )

            except Exception as e:

                st.error(f"Error RSI: {e}")

# ====================================
# FUNDAMENTAL
# ====================================

elif menu == "Fundamental":

    st.title("📊 Fundamental")

    market = st.selectbox(
        "Pilih Market Fundamental",
        ["US", "Indonesia"]
    )

    ticker = st.text_input(
        "Masukkan Saham",
        "AAPL"
    )

    if st.button("Tampilkan Fundamental"):

        if market == "Indonesia":
            ticker_final = ticker.upper() + ".JK"
        else:
            ticker_final = ticker.upper()

        df, info = get_stock_data(ticker_final)

        if not info:

            st.error("Data fundamental gagal dimuat")

        else:

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

            st.success("Fundamental berhasil dimuat")

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
