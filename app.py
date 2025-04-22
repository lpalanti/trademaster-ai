import streamlit as st
import pandas as pd
import requests
import yfinance as yf
from plotly import graph_objs as go

st.set_page_config(layout="wide")
st.title("📈 TradeMaster AI")

@st.cache_data(ttl=180)
def get_usd_brl():
    try:
        data = yf.download("USDBRL=X", period="1d", interval="1m")
        return data["Close"].iloc[-1]
    except Exception as e:
        st.error(f"Erro ao buscar cotação do USD/BRL: {e}")
        return 5.0  # Valor padrão em caso de erro

usd_brl = get_usd_brl()

def plot_candlestick(df, nome):
    if df.empty: return
    fig = go.Figure(data=[go.Candlestick(
        x=df.index,
        open=df['Open'],
        high=df['High'],
        low=df['Low'],
        close=df['Close']
    )])
    fig.update_layout(title=f"📊 Gráfico de Velas - {nome}", xaxis_rangeslider_visible=False, height=400)
    st.plotly_chart(fig, use_container_width=True)

# ======= CRIPTOS =======
CRYPTO = {
    "Bitcoin": "bitcoin", "Ethereum": "ethereum", "Ripple": "ripple", "Dogecoin": "dogecoin",
    "Litecoin": "litecoin", "Cardano": "cardano", "Polkadot": "polkadot", "Solana": "solana",
    "Avalanche": "avalanche-2", "Chainlink": "chainlink", "Shiba Inu": "shiba-inu",
    "Binance Coin": "binancecoin", "Polygon": "matic-network", "Uniswap": "uniswap", "Terra": "terra-luna"
}

def fetch_crypto_data(coin_id, usd_brl):
    try:
        url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/ohlc?vs_currency=usd&days=1"
        r = requests.get(url).json()
        if not r: return pd.DataFrame(), {}

        df = pd.DataFrame(r, columns=["timestamp", "Open", "High", "Low", "Close"])
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
        df.set_index("timestamp", inplace=True)
        df[["Open", "High", "Low", "Close"]] *= usd_brl

        max_price = df["High"].max()
        min_price = df["Low"].min()
        vol = max_price - min_price
        vol_pct = (vol / min_price) * 100
        buy = min_price + 0.1 * vol
        sell = max_price - 0.1 * vol

        return df, {
            "Volatilidade": f"R$ {vol:.2f}",
            "% Volatilidade": f"{vol_pct:.2f}%",
            "Menor Preço do Dia": f"R$ {min_price:.2f}",
            "Maior Preço do Dia": f"R$ {max_price:.2f}",
            "Ideal Compra": f"R$ {buy:.2f}",
            "Ideal Venda": f"R$ {sell:.2f}"
        }
    except Exception as e:
        st.error(f"Erro ao buscar dados de criptomoeda: {coin_id} - {e}")
        return pd.DataFrame(), {}

# ======= AÇÕES =======
STOCKS = [
    "TSLA", "AMZN", "AAPL", "META", "NFLX", "NVDA", "GME", "AMC", "SPOT",
    "PLTR", "ROKU", "SQ", "ZM", "DOCU", "BYND", "COIN", "HOOD", "MRNA", "SNOW"
]

def fetch_yahoo_data(ticker, usd_brl):
    try:
        df = yf.download(ticker, period="1d", interval="5m")
        if df.empty: return pd.DataFrame(), {}

        df[["Open", "High", "Low", "Close"]] *= usd_brl
        max_price = df["High"].max()
        min_price = df["Low"].min()
        vol = max_price - min_price
        vol_pct = (vol / min_price) * 100
        buy = min_price + 0.1 * vol
        sell = max_price - 0.1 * vol

        return df, {
            "Volatilidade": f"R$ {vol:.2f}",
            "% Volatilidade": f"{vol_pct:.2f}%",
            "Menor Preço do Dia": f"R$ {min_price:.2f}",
            "Maior Preço do Dia": f"R$ {max_price:.2f}",
            "Ideal Compra": f"R$ {buy:.2f}",
            "Ideal Venda": f"R$ {sell:.2f}"
        }
    except Exception as e:
        st.error(f"Erro ao buscar dados da ação: {ticker} - {e}")
        return pd.DataFrame(), {}

# ======= COMMODITIES =======
COMMODITIES = {
    "Ouro": "GC=F", "Brent": "BZ=F", "WTI": "CL=F", "Cobre": "HG=F",
    "Algodão": "CT=F", "Café": "KC=F", "Soja": "ZS=F", "Milho": "ZC=F",
    "Açúcar": "SB=F", "Paládio": "PA=F"
}

st.header("💰 Criptomoedas")
crypto_data = []
for nome, coin_id in CRYPTO.items():
    df, info = fetch_crypto_data(coin_id, usd_brl)
    if info:
        info["Ativo"] = nome
        crypto_data.append(info)

st.dataframe(pd.DataFrame(crypto_data), use_container_width=True)
for nome, coin_id in CRYPTO.items():
    df, _ = fetch_crypto_data(coin_id, usd_brl)
    plot_candlestick(df, nome)

st.header("📊 Ações")
stock_data = []
for ticker in STOCKS:
    df, info = fetch_yahoo_data(ticker, usd_brl)
    if info:
        info["Ativo"] = ticker
        stock_data.append(info)

st.dataframe(pd.DataFrame(stock_data), use_container_width=True)
for ticker in STOCKS:
    df, _ = fetch_yahoo_data(ticker, usd_brl)
    plot_candlestick(df, ticker)

st.header("🛢️ Commodities")
commodity_data = []
for nome, ticker in COMMODITIES.items():
    df, info = fetch_yahoo_data(ticker, usd_brl)
    if info:
        info["Ativo"] = nome
        commodity_data.append(info)

st.dataframe(pd.DataFrame(commodity_data), use_container_width=True)
for nome, ticker in COMMODITIES.items():
    df, _ = fetch_yahoo_data(ticker, usd_brl)
    plot_candlestick(df, nome)
