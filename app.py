import streamlit as st
import requests
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go

st.set_page_config(page_title="TradeMaster AI", layout="centered")
st.title("📊 TradeMaster AI — Painel de Ativos em Reais (R$)")

# Dicionários de ativos
CRYPTO = {
    "Bitcoin": "bitcoin",
    "Ethereum": "ethereum",
    "Ripple": "ripple",
    "Dogecoin": "dogecoin",
    "Litecoin": "litecoin",
    "Cardano": "cardano",
    "Polkadot": "polkadot",
    "Solana": "solana",
    "Avalanche": "avalanche-2",
    "Chainlink": "chainlink",
    "Shiba Inu": "shiba-inu",
    "Binance Coin": "binancecoin",
    "Polygon": "polygon",
    "Uniswap": "uniswap",
    "Terra": "terra-luna"
}

STOCKS = {
    "Tesla": "TSLA",
    "Amazon": "AMZN",
    "Apple": "AAPL",
    "Meta": "META",
    "Netflix": "NFLX",
    "Nvidia": "NVDA",
    "GameStop": "GME",
    "AMC Entertainment": "AMC",
    "Spotify": "SPOT",
    "Palantir": "PLTR",
    "Roku": "ROKU",
    "Square": "SQ",
    "Zoom Video": "ZM",
    "DocuSign": "DOCU",
    "Beyond Meat": "BYND",
    "Coinbase": "COIN",
    "Robinhood": "HOOD",
    "Moderna": "MRNA",
    "Snowflake": "SNOW"
}

COMMODITIES = {
    "Ouro (XAU)": "GC=F",
    "Petróleo Brent": "BZ=F",
    "Petróleo WTI": "CL=F",
    "Cobre": "HG=F",
    "Algodão": "CT=F",
    "Café": "KC=F",
    "Soja": "ZS=F",
    "Milho": "ZC=F",
    "Açúcar": "SB=F",
    "Paládio": "PA=F"
}

# Preço do dólar
def get_usd_brl():
    url = "https://economia.awesomeapi.com.br/last/USD-BRL"
    try:
        r = requests.get(url).json()
        return float(r['USDBRL']['bid'])
    except:
        return 5.0

# Cripto via CoinGecko
def fetch_crypto_data(coin_id, usd_brl):
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart?vs_currency=usd&days=1&interval=hourly"
    r = requests.get(url).json()
    prices = r["prices"]
    df = pd.DataFrame(prices, columns=["timestamp", "price"])
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
    df["price_brl"] = df["price"] * usd_brl

    max_price = df["price_brl"].max()
    min_price = df["price_brl"].min()
    volatility = max_price - min_price
    volatility_pct = (volatility / min_price) * 100
    ideal_buy = min_price + 0.1 * volatility
    ideal_sell = max_price - 0.1 * volatility

    return df, {
        "Volatilidade": f"R$ {volatility:.2f}",
        "% Volatilidade": f"{volatility_pct:.2f}%",
        "Menor Preço do Dia": f"R$ {min_price:.2f}",
        "Maior Preço do Dia": f"R$ {max_price:.2f}",
        "Ideal Compra": f"R$ {ideal_buy:.2f}",
        "Ideal Venda": f"R$ {ideal_sell:.2f}"
    }

# Ações e Commodities via Yahoo Finance
def fetch_yfinance_data(symbol, usd_brl):
    ticker = yf.Ticker(symbol)
    df = ticker.history(period="1d", interval="15m")
    if df.empty:
        return pd.DataFrame(), {}

    df.reset_index(inplace=True)
    df["price_brl"] = df["Close"] * usd_brl

    max_price = df["price_brl"].max()
    min_price = df["price_brl"].min()
    volatility = max_price - min_price
    volatility_pct = (volatility / min_price) * 100
    ideal_buy = min_price + 0.1 * volatility
    ideal_sell = max_price - 0.1 * volatility

    return df, {
        "Volatilidade": f"R$ {volatility:.2f}",
        "% Volatilidade": f"{volatility_pct:.2f}%",
        "Menor Preço do Dia": f"R$ {min_price:.2f}",
        "Maior Preço do Dia": f"R$ {max_price:.2f}",
        "Ideal Compra": f"R$ {ideal_buy:.2f}",
        "Ideal Venda": f"R$ {ideal_sell:.2f}"
    }

def plot_candlestick(df, is_crypto=False):
    if is_crypto:
        df["Open"] = df["price_brl"]
        df["High"] = df["price_brl"]
        df["Low"] = df["price_brl"]
        df["Close"] = df["price_brl"]
        df["Datetime"] = df["timestamp"]
    else:
        df["Datetime"] = df["Datetime"]

    fig = go.Figure(data=[go.Candlestick(
        x=df["Datetime"],
        open=df["Open"],
        high=df["High"],
        low=df["Low"],
        close=df["Close"]
    )])
    fig.update_layout(xaxis_rangeslider_visible=False, height=300)
    return fig

# ================== INTERFACE ==================

usd_brl = get_usd_brl()
st.markdown(f"💵 Cotação do dólar: **R$ {usd_brl:.2f}**")

# Painel Cripto
st.header("💰 Criptomoedas")
crypto_data = []
for name, coin_id in CRYPTO.items():
    df, info = fetch_crypto_data(coin_id, usd_brl)
    info["Ativo"] = name
    crypto_data.append(info)
df_crypto_table = pd.DataFrame(crypto_data).set_index("Ativo")
st.dataframe(df_crypto_table, use_container_width=True)
for name, coin_id in CRYPTO.items():
    df, _ = fetch_crypto_data(coin_id, usd_brl)
    st.subheader(f"📉 {name}")
    st.plotly_chart(plot_candlestick(df, is_crypto=True), use_container_width=True)

# Painel Ações
st.header("📈 Ações")
stocks_data = []
for name, ticker in STOCKS.items():
    df, info = fetch_yfinance_data(ticker, usd_brl)
    if info:
        info["Ativo"] = name
        stocks_data.append(info)
df_stocks_table = pd.DataFrame(stocks_data).set_index("Ativo")
st.dataframe(df_stocks_table, use_container_width=True)
for name, ticker in STOCKS.items():
    df, _ = fetch_yfinance_data(ticker, usd_brl)
    if not df.empty:
        st.subheader(f"📉 {name}")
        st.plotly_chart(plot_candlestick(df), use_container_width=True)

# Painel Commodities
st.header("🛢️ Commodities")
commodities_data = []
for name, ticker in COMMODITIES.items():
    df, info = fetch_yfinance_data(ticker, usd_brl)
    if info:
        info["Ativo"] = name
        commodities_data.append(info)
df_commodities_table = pd.DataFrame(commodities_data).set_index("Ativo")
st.dataframe(df_commodities_table, use_container_width=True)
for name, ticker in COMMODITIES.items():
    df, _ = fetch_yfinance_data(ticker, usd_brl)
    if not df.empty:
        st.subheader(f"📉 {name}")
        st.plotly_chart(plot_candlestick(df), use_container_width=True)
