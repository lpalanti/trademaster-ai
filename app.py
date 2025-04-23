import streamlit as st
import pandas as pd
import yfinance as yf
from pycoingecko import CoinGeckoAPI
import requests

# Telegram config
TELEGRAM_TOKEN = '7971840892:AAH8sIg3iQUI7jQkMSd3YrYPaU4giRDVRQc'
CHAT_ID = '1963421158'

def send_telegram_alert(message):
    url = f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage'
    data = {'chat_id': CHAT_ID, 'text': message}
    requests.post(url, data=data)

# Painel Cripto
def painel_cripto():
    st.subheader("Painel Criptomoedas")
    cg = CoinGeckoAPI()
    coins = ["bitcoin", "ethereum", "ripple", "cardano", "litecoin", 
             "solana", "polkadot", "chainlink", "avalanche-2", "uniswap"]
    cripto_data = []

    for coin in coins:
        try:
            data = cg.get_price(ids=coin, vs_currencies='brl', include_24hr_change=True)
            price = data[coin]['brl']
            change = data[coin]['brl_24h_change']
            preco_compra = price * 0.95
            preco_venda = price * 1.05

            if price <= preco_compra:
                send_telegram_alert(f"🚨 Cripto em oportunidade!\n{coin.upper()} abaixo do ideal de compra.\n💰 Atual: R$ {price:.2f}\n🎯 Alvo: R$ {preco_compra:.2f}")

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

# Painel Ações
def painel_acoes():
    st.subheader("Painel Ações")
    stock_list = [
        "PETR4.SA", "VALE3.SA", "ITUB4.SA", "BBDC4.SA", "WEGE3.SA",
        "ABEV3.SA", "BBAS3.SA", "MGLU3.SA", "RENT3.SA", "RAIL3.SA"
    ]
    stock_data = []

    for ticker in stock_list:
        try:
            stock = yf.Ticker(ticker)
            df = stock.history(period="1d", interval="1m")

            if df.empty:
                continue

            price = df['Close'][-1]
            preco_compra = price * 0.95
            preco_venda = price * 1.05

            if price <= preco_compra:
                send_telegram_alert(f"📉 Ação em oportunidade!\n{ticker} abaixo do ideal de compra.\n💰 Atual: R$ {price:.2f}\n🎯 Alvo: R$ {preco_compra:.2f}")

            stock_data.append({
                "Ação": ticker,
                "Preço atual (R$)": f"R$ {price:.2f}",
                "Sugestão Compra (R$)": f"R$ {preco_compra:.2f}",
                "Sugestão Venda (R$)": f"R$ {preco_venda:.2f}"
            })
        except Exception as e:
            st.warning(f"Erro em {ticker}: {e}")

    df = pd.DataFrame(stock_data)
    st.table(df)

# Painel Commodities
def painel_commodities():
    st.subheader("Painel Commodities")
    commodities = ["GC=F", "SI=F", "CL=F", "BZ=F", "NG=F"]
    commodities_data = []

    for commodity in commodities:
        try:
            com = yf.Ticker(commodity)
            df = com.history(period="1d", interval="1m")

            if df.empty:
                continue

            price = df['Close'][-1]
            preco_compra = price * 0.95
            preco_venda = price * 1.05

            if price <= preco_compra:
                send_telegram_alert(f"🛢️ Commodity em oportunidade!\n{commodity} abaixo do ideal de compra.\n💰 Atual: R$ {price:.2f}\n🎯 Alvo: R$ {preco_compra:.2f}")

            commodities_data.append({
                "Commodity": commodity,
                "Preço atual (R$)": f"R$ {price:.2f}",
                "Sugestão Compra (R$)": f"R$ {preco_compra:.2f}",
                "Sugestão Venda (R$)": f"R$ {preco_venda:.2f}"
            })
        except Exception as e:
            st.warning(f"Erro em {commodity}: {e}")

    df = pd.DataFrame(commodities_data)
    st.table(df)

# App
st.title("📊 Painel de Análise de Ativos")

aba = st.radio("Selecione o tipo de ativo:", ["Criptomoedas", "Ações", "Commodities"])

if aba == "Criptomoedas":
    painel_cripto()
elif aba == "Ações":
    painel_acoes()
elif aba == "Commodities":
    painel_commodities()
