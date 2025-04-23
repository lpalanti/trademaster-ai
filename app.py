import streamlit as st
import pandas as pd
import yfinance as yf
from pycoingecko import CoinGeckoAPI

cg = CoinGeckoAPI()

st.set_page_config(layout="wide")
st.title("📊 TradeMaster AI - Painéis de Acompanhamento")

# Função para carregar dados de criptomoedas via CoinGecko
def carregar_dados_cripto(ativos):
    tabela = []

    try:
        usd_brl = cg.get_price(ids="usd", vs_currencies="brl")["usd"]["brl"]
    except:
        st.error("Erro ao obter taxa USD/BRL.")
        return pd.DataFrame()

    for nome, coin_id in ativos.items():
        try:
            info = cg.get_coin_by_id(coin_id, localization=False)
            preco = info["market_data"]["current_price"]["brl"]
            maximo = info["market_data"]["high_24h"]["brl"]
            minimo = info["market_data"]["low_24h"]["brl"]
            vol = info["market_data"]["price_change_percentage_24h"]

            preco_compra = preco * 0.95
            preco_venda = preco * 1.05

            tabela.append({
                "Nome": nome,
                "Preço (R$)": f"R$ {preco:.2f}",
                "Máximo 24h": f"R$ {maximo:.2f}",
                "Mínimo 24h": f"R$ {minimo:.2f}",
                "Variação 24h (%)": f"{vol:.2f}%",
                "Sugestão de Compra": f"R$ {preco_compra:.2f}",
                "Sugestão de Venda": f"R$ {preco_venda:.2f}",
            })
        except:
            continue

    return pd.DataFrame(tabela)

# Função para carregar dados de ações e commodities via Yahoo Finance
def carregar_dados_yahoo(ativos):
    tabela = []

    for nome, ticker in ativos.items():
        try:
            dado = yf.Ticker(ticker)
            hist = dado.history(period="1d", interval="1m")
            preco_atual = hist["Close"][-1]
            minimo = hist["Low"].min()
            maximo = hist["High"].max()
            vol = (maximo - minimo) / preco_atual * 100 if preco_atual != 0 else 0

            preco_compra = preco_atual * 0.95
            preco_venda = preco_atual * 1.05

            tabela.append({
                "Nome": nome,
                "Preço (R$)": f"R$ {preco_atual:.2f}",
                "Máximo 24h": f"R$ {maximo:.2f}",
                "Mínimo 24h": f"R$ {minimo:.2f}",
                "Variação (%)": f"{vol:.2f}%",
                "Sugestão de Compra": f"R$ {preco_compra:.2f}",
                "Sugestão de Venda": f"R$ {preco_venda:.2f}",
            })
        except:
            continue

    return pd.DataFrame(tabela)

# Dicionários de ativos
cripto = {
    "Bitcoin (BTC)": "bitcoin",
    "Ethereum (ETH)": "ethereum",
    "Ripple (XRP)": "ripple",
    "Dogecoin (DOGE)": "dogecoin",
    "Litecoin (LTC)": "litecoin",
    "Cardano (ADA)": "cardano",
    "Polkadot (DOT)": "polkadot",
    "Solana (SOL)": "solana",
    "Avalanche (AVAX)": "avalanche-2",
    "Chainlink (LINK)": "chainlink",
    "Shiba Inu (SHIB)": "shiba-inu",
    "Binance Coin (BNB)": "binancecoin",
    "Polygon (MATIC)": "matic-network",
    "Uniswap (UNI)": "uniswap",
    "Terra (LUNA)": "terra-luna"
}

acoes = {
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

# Interface
st.subheader("🔍 Selecione a categoria que deseja visualizar:")

col1, col2, col3 = st.columns(3)
mostrar_cripto = col1.button("💰 Criptomoedas")
mostrar_acoes = col2.button("📈 Ações")
mostrar_commodities = col3.button("🌾 Commodities")

if mostrar_cripto:
    st.subheader("💰 Painel de Criptomoedas")
    df_cripto = carregar_dados_cripto(cripto)
    st.dataframe(df_cripto, use_container_width=True)

if mostrar_acoes:
    st.subheader("📈 Painel de Ações")
    df_acoes = carregar_dados_yahoo(acoes)
    st.dataframe(df_acoes, use_container_width=True)

if mostrar_commodities:
    st.subheader("🌾 Painel de Commodities")
    df_commodities = carregar_dados_yahoo(commodities)
    st.dataframe(df_commodities, use_container_width=True)

