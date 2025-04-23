import streamlit as st
import pandas as pd
import yfinance as yf
from pycoingecko import CoinGeckoAPI

cg = CoinGeckoAPI()

# Conversão USD → BRL
def get_usd_brl():
    ticker = yf.Ticker("USDBRL=X")
    data = ticker.history(period="1d", interval="1m")
    return data["Close"].iloc[-1]

usd_brl = get_usd_brl()

# --- LISTAS DE ATIVOS ---
cripto_ids = {
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

acoes = [
    "TSLA", "AMZN", "AAPL", "META", "NFLX", "NVDA", "GME", "AMC",
    "SPOT", "PLTR", "ROKU", "SQ", "ZM", "DOCU", "BYND", "COIN",
    "HOOD", "MRNA", "SNOW"
]

commodities = {
    "Ouro": "GC=F",
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

# --- FUNÇÕES ---
def painel_cripto():
    dados = []
    for nome, coin_id in cripto_ids.items():
        try:
            data = cg.get_coin_market_chart_by_id(id=coin_id, vs_currency='usd', days=1)
            preco = data["prices"][-1][1]
            high = max([x[1] for x in data["prices"]])
            low = min([x[1] for x in data["prices"]])
            vol = ((high - low) / low) * 100
            compra = low * 1.05
            venda = high * 0.95
            dados.append({
                "Cripto": nome,
                "Menor Preço": f"R$ {low * usd_brl:.2f}",
                "Maior Preço": f"R$ {high * usd_brl:.2f}",
                "Preço Atual": f"R$ {preco * usd_brl:.2f}",
                "Volatilidade (%)": f"{vol:.2f}%",
                "Compra Ideal": f"R$ {compra * usd_brl:.2f}",
                "Venda Ideal": f"R$ {venda * usd_brl:.2f}"
            })
        except Exception as e:
            continue
    return pd.DataFrame(dados)

def painel_acoes():
    dados = []
    for ticker in acoes:
        try:
            acao = yf.Ticker(ticker)
            hist = acao.history(period="1d", interval="1m")
            preco = hist["Close"].iloc[-1]
            high = hist["High"].max()
            low = hist["Low"].min()
            vol = ((high - low) / low) * 100
            compra = low * 1.05
            venda = high * 0.95
            dados.append({
                "Ação": ticker,
                "Menor Preço": f"R$ {low * usd_brl:.2f}",
                "Maior Preço": f"R$ {high * usd_brl:.2f}",
                "Preço Atual": f"R$ {preco * usd_brl:.2f}",
                "Volatilidade (%)": f"{vol:.2f}%",
                "Compra Ideal": f"R$ {compra * usd_brl:.2f}",
                "Venda Ideal": f"R$ {venda * usd_brl:.2f}"
            })
        except Exception as e:
            continue
    return pd.DataFrame(dados)

def painel_commodities():
    dados = []
    for nome, ticker in commodities.items():
        try:
            com = yf.Ticker(ticker)
            hist = com.history(period="1d", interval="1m")
            preco = hist["Close"].iloc[-1]
            high = hist["High"].max()
            low = hist["Low"].min()
            vol = ((high - low) / low) * 100
            compra = low * 1.05
            venda = high * 0.95
            dados.append({
                "Commodity": nome,
                "Menor Preço": f"R$ {low * usd_brl:.2f}",
                "Maior Preço": f"R$ {high * usd_brl:.2f}",
                "Preço Atual": f"R$ {preco * usd_brl:.2f}",
                "Volatilidade (%)": f"{vol:.2f}%",
                "Compra Ideal": f"R$ {compra * usd_brl:.2f}",
                "Venda Ideal": f"R$ {venda * usd_brl:.2f}"
            })
        except Exception as e:
            continue
    return pd.DataFrame(dados)

# --- INTERFACE ---
st.set_page_config(layout="wide")
st.title("📊 TradeMaster.AI - Painel de Ativos em Reais")

st.subheader("🪙 Criptomoedas")
st.dataframe(painel_cripto(), use_container_width=True)

st.subheader("📈 Ações")
st.dataframe(painel_acoes(), use_container_width=True)

st.subheader("🛢️ Commodities")
st.dataframe(painel_commodities(), use_container_width=True)

