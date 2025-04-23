import streamlit as st
import pandas as pd
import yfinance as yf
import requests
from datetime import datetime
import pytz

# Função para converter USD para BRL
def get_usd_brl():
    url = "https://api.exchangerate.host/latest?base=USD&symbols=BRL"
    response = requests.get(url)
    data = response.json()
    return data["rates"]["BRL"]

# Função para calcular preços sugeridos
def calc_sugestoes(preco):
    preco_compra = preco * 0.95
    preco_venda = preco * 1.05
    return preco_compra, preco_venda

# Criptomoedas (usando CoinGecko)
crypto_ids = {
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
    "Polygon": "matic-network",
    "Uniswap": "uniswap",
    "Terra": "terra-luna"
}

# Ações
stock_tickers = {
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

# Commodities (yfinance)
commodity_tickers = {
    "Ouro": "XAUUSD=X",
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

usd_brl = get_usd_brl()

# Função dados CoinGecko
def fetch_crypto_data():
    df = []
    for name, coin_id in crypto_ids.items():
        try:
            r = requests.get(f"https://api.coingecko.com/api/v3/coins/{coin_id}?localization=false&tickers=false&market_data=true&community_data=false&developer_data=false&sparkline=false")
            r = r.json()
            preco_usd = r["market_data"]["current_price"]["usd"]
            preco_brl = preco_usd * usd_brl
            preco_min = r["market_data"]["low_24h"]["usd"] * usd_brl
            preco_max = r["market_data"]["high_24h"]["usd"] * usd_brl
            variacao = r["market_data"]["price_change_percentage_24h"]
            preco_compra, preco_venda = calc_sugestoes(preco_brl)
            df.append({
                "Nome": name,
                "Sigla": coin_id.upper(),
                "Preço (R$)": f"R$ {preco_brl:,.2f}",
                "Menor Preço (R$)": f"R$ {preco_min:,.2f}",
                "Maior Preço (R$)": f"R$ {preco_max:,.2f}",
                "Variação (%)": f"{variacao:.2f}%",
                "Preço Compra Sugerido": f"R$ {preco_compra:,.2f}",
                "Preço Venda Sugerido": f"R$ {preco_venda:,.2f}"
            })
        except:
            continue
    return pd.DataFrame(df)

# Função dados yFinance
def fetch_yahoo_data(tickers_dict):
    df = []
    for name, ticker in tickers_dict.items():
        try:
            data = yf.Ticker(ticker).history(period="1d", interval="1m")
            preco = data["Close"].iloc[-1] * usd_brl
            menor = data["Low"].min() * usd_brl
            maior = data["High"].max() * usd_brl
            variacao = ((maior - menor) / menor) * 100
            preco_compra, preco_venda = calc_sugestoes(preco)
            df.append({
                "Nome": name,
                "Sigla": ticker,
                "Preço (R$)": f"R$ {preco:,.2f}",
                "Menor Preço (R$)": f"R$ {menor:,.2f}",
                "Maior Preço (R$)": f"R$ {maior:,.2f}",
                "Variação (%)": f"{variacao:.2f}%",
                "Preço Compra Sugerido": f"R$ {preco_compra:,.2f}",
                "Preço Venda Sugerido": f"R$ {preco_venda:,.2f}"
            })
        except:
            continue
    return pd.DataFrame(df)

# Interface
st.set_page_config(layout="wide")
st.title("📊 Painel de Análise de Ativos")

aba = st.sidebar.radio("Escolha o Painel:", ("Criptomoedas", "Ações", "Commodities"))

if aba == "Criptomoedas":
    st.header("🪙 Criptomoedas")
    df = fetch_crypto_data()
    st.dataframe(df, use_container_width=True)

elif aba == "Ações":
    st.header("📈 Ações")
    df = fetch_yahoo_data(stock_tickers)
    st.dataframe(df, use_container_width=True)

elif aba == "Commodities":
    st.header("🛢️ Commodities")
    df = fetch_yahoo_data(commodity_tickers)
    st.dataframe(df, use_container_width=True)
