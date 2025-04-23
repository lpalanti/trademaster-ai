import streamlit as st
import pandas as pd
import yfinance as yf
from pycoingecko import CoinGeckoAPI
import requests

# Configurações do Telegram
TELEGRAM_TOKEN = '7971840892:AAH8sIg3iQUI7jQkMSd3YrYPaU4giRDVRQc'
CHAT_ID = '1963421158'

def send_telegram_alert(message):
    url = f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage'
    data = {'chat_id': CHAT_ID, 'text': message}
    requests.post(url, data=data)

# Função painel Cripto
def painel_cripto():
    st.subheader("Painel Criptomoedas")
    cg = CoinGeckoAPI()
    coins = [
        "bitcoin", "ethereum", "ripple", "dogecoin", "litecoin",
        "cardano", "polkadot", "solana", "avalanche", "chainlink",
        "shiba-inu", "binancecoin", "polygon", "uniswap", "terra-luna"
    ]
    cripto_data = []

    for coin in coins:
        try:
            data = cg.get_price(ids=coin, vs_currencies='brl', include_24hr_change=True)
            price = data[coin]['brl']
            change = data[coin]['brl_24h_change']
            preco_compra = price * 0.95
            preco_venda = price * 1.05

            if price <= preco_compra:
                send_telegram_alert(
                    f"🚨 Cripto em oportunidade!\n"
                    f"{coin.upper()} abaixo do ideal de compra.\n"
                    f"💰 Atual: R$ {price:.2f}\n"
                    f"🎯 Alvo: R$ {preco_compra:.2f}"
                )

            cripto_data.append({
                "Cripto": coin.upper(),
                "Preço atual (R$)": f"R$ {price:.2f}",
                "Variação 24h (%)": f"{change:.2f}%",
                "Sugestão Compra (R$)": f"R$ {preco_compra:.2f}",
                "Sugestão Venda (R$)": f"R$ {preco_venda:.2f}"
            })
        except Exception as e:
            st.warning(f"Erro ao buscar {coin}: {e}")

    df = pd.DataFrame(cripto_data)
    st.table(df)

# Função painel Ações
def painel_acoes():
    st.subheader("Painel Ações")
    stock_list = [
        "TSLA", "AMZN", "AAPL", "META", "NFLX", "NVDA", "GME", "AMC", "SPOT",
        "PLTR", "ROKU", "SQ", "ZM", "DOCU", "BYND", "COIN", "HOOD", "MRNA", "SNOW"
    ]
    stock_data = []

    for ticker in stock_list:
        try:
            stock = yf.Ticker(ticker)
            df_hist = stock.history(period="1d", interval="1m")
            if df_hist.empty:
                continue

            price = df_hist['Close'][-1]
            low = df_hist['Low'].min()
            high = df_hist['High'].max()
            change = ((price - df_hist['Open'][0]) / df_hist['Open'][0]) * 100
            preco_compra = price * 0.95
            preco_venda = price * 1.05

            if price <= preco_compra:
                send_telegram_alert(
                    f"📉 Ação em oportunidade!\n"
                    f"{ticker} abaixo do ideal de compra.\n"
                    f"💰 Atual: R$ {price:.2f}\n"
                    f"🎯 Alvo: R$ {preco_compra:.2f}"
                )

            stock_data.append({
                "Ação": ticker,
                "Preço Atual (R$)": f"R$ {price:.2f}",
                "Mínimo do Dia (R$)": f"R$ {low:.2f}",
                "Máximo do Dia (R$)": f"R$ {high:.2f}",
                "Variação (%)": f"{change:.2f}%",
                "Sugestão Compra (R$)": f"R$ {preco_compra:.2f}",
                "Sugestão Venda (R$)": f"R$ {preco_venda:.2f}"
            })
        except Exception as e:
            st.warning(f"Erro em {ticker}: {e}")

    df = pd.DataFrame(stock_data)
    st.table(df)

# Função painel Commodities
def painel_commodities():
    st.subheader("Painel Commodities")
    commodity_list = [
        "XAUUSD=X", "BZ=F", "CL=F", "HG=F", "CT=F", "KC=F", "ZS=F", "ZC=F", "SB=F", "PA=F"
    ]
    commodities_data = []

    for commodity in commodity_list:
        try:
            com = yf.Ticker(commodity)
            df_hist = com.history(period="1d", interval="1m")
            if df_hist.empty:
                continue

            price = df_hist['Close'][-1]
            low = df_hist['Low'].min()
            high = df_hist['High'].max()
            change = ((price - df_hist['Open'][0]) / df_hist['Open'][0]) * 100
            preco_compra = price * 0.95
            preco_venda = price * 1.05

            if price <= preco_compra:
                send_telegram_alert(
                    f"🛢️ Commodity em oportunidade!\n"
                    f"{commodity} abaixo do ideal de compra.\n"
                    f"💰 Atual: R$ {price:.2f}\n"
                    f"🎯 Alvo: R$ {preco_compra:.2f}"
                )

            commodities_data.append({
                "Commodity": commodity,
                "Preço Atual (R$)": f"R$ {price:.2f}",
                "Mínimo do Dia (R$)": f"R$ {low:.2f}",
                "Máximo do Dia (R$)": f"R$ {high:.2f}",
                "Variação (%)": f"{change:.2f}%",
                "Sugestão Compra (R$)": f"R$ {preco_compra:.2f}",
                "Sugestão Venda (R$)": f"R$ {preco_venda:.2f}"
            })
        except Exception as e:
            st.warning(f"Erro em {commodity}: {e}")

    df = pd.DataFrame(commodities_data)
    st.table(df)

# Interface principal
st.title("🔎 Painel de Análise de Ativos")

aba = st.radio("Selecione o tipo de ativo:", ["Criptomoedas", "Ações", "Commodities"])

if aba == "Criptomoedas":
    painel_cripto()
elif aba == "Ações":
    painel_acoes()
elif aba == "Commodities":
    painel_commodities()
