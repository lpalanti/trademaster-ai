import streamlit as st
import requests
import yfinance as yf
import pandas as pd

# Função para obter dados de criptoativos
@st.cache_data(ttl=180)  # Cache com tempo de expiração de 180 segundos (3 minutos)
def get_cripto_data():
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {
        'vs_currency': 'usd',
        'ids': 'bitcoin,ethereum,ripple,dogecoin,litecoin,cardano,polkadot,solana,avalanche,chainlink,shiba-inu,binancecoin,polygon,uniswap,terra',
        'order': 'market_cap_desc'
    }
    response = requests.get(url, params=params)
    data = response.json()
    return pd.DataFrame(data)

# Função para obter dados de ações
@st.cache_data(ttl=180)  # Cache com tempo de expiração de 180 segundos (3 minutos)
def get_stock_data():
    tickers = [
        "TSLA", "AMZN", "AAPL", "META", "NFLX", "NVDA", "GME", "AMC", "SPOT", "PLTR",
        "ROKU", "SQ", "ZM", "DOCU", "BYND", "COIN", "HOOD", "MRNA", "SNOW"
    ]
    data = {}
    for ticker in tickers:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="1d")
        data[ticker] = {
            "volatility": hist['Close'].pct_change().std() * 100,
            "lowest_price": hist['Low'].iloc[0],
            "highest_price": hist['High'].iloc[0],
            "buy_price": hist['Close'].iloc[0] * 0.98,  # Exemplo de preço de compra
            "sell_price": hist['Close'].iloc[0] * 1.02  # Exemplo de preço de venda
        }
    return data

# Função para obter dados de commodities
@st.cache_data(ttl=180)  # Cache com tempo de expiração de 180 segundos (3 minutos)
def get_commodities_data():
    commodities = {
        "Gold": "XAU/USD",
        "Brent Crude Oil": "BZ=F",
        "WTI Crude Oil": "CL=F",
        "Copper": "HG=F",
        "Cotton": "CT=F",
        "Coffee": "KC=F",
        "Soybeans": "ZS=F",
        "Corn": "ZC=F",
        "Sugar": "SB=F",
        "Palladium": "PA=F"
    }
    data = {}
    for name, symbol in commodities.items():
        commodity = yf.Ticker(symbol)
        hist = commodity.history(period="1d")
        data[name] = {
            "volatility": hist['Close'].pct_change().std() * 100,
            "lowest_price": hist['Low'].iloc[0],
            "highest_price": hist['High'].iloc[0],
            "buy_price": hist['Close'].iloc[0] * 0.98,  # Exemplo de preço de compra
            "sell_price": hist['Close'].iloc[0] * 1.02  # Exemplo de preço de venda
        }
    return data

# Página Inicial
st.title('Day Trade Dashboard')

# Botões
selected_option = st.radio("Escolha o tipo de mercado:", ("Day Trade Cripto", "Day Trade Ações", "Day Trade Commodities"))

# Exibição dos dados de Cripto
if selected_option == "Day Trade Cripto":
    st.subheader("Criptoativos")
    cripto_data = get_cripto_data()
    for index, row in cripto_data.iterrows():
        st.write(f"**{row['name']}**")
        st.write(f"Volatilidade: {row['price_change_percentage_24h']}%")
        st.write(f"Menor preço do dia: {row['low_24h']}")
        st.write(f"Maior preço do dia: {row['high_24h']}")
        st.write(f"Preço ideal de compra: {row['buy_price']}")
        st.write(f"Preço ideal de venda: {row['sell_price']}")
        st.write("----")

# Exibição dos dados de Ações
elif selected_option == "Day Trade Ações":
    st.subheader("Ações")
    stock_data = get_stock_data()
    for ticker, info in stock_data.items():
        st.write(f"**{ticker}**")
        st.write(f"Volatilidade: {info['volatility']}%")
        st.write(f"Menor preço do dia: {info['lowest_price']}")
        st.write(f"Maior preço do dia: {info['highest_price']}")
        st.write(f"Preço ideal de compra: {info['buy_price']}")
        st.write(f"Preço ideal de venda: {info['sell_price']}")
        st.write("----")

# Exibição dos dados de Commodities
elif selected_option == "Day Trade Commodities":
    st.subheader("Commodities")
    commodities_data = get_commodities_data()
    for name, info in commodities_data.items():
        st.write(f"**{name}**")
        st.write(f"Volatilidade: {info['volatility']}%")
        st.write(f"Menor preço do dia: {info['lowest_price']}")
        st.write(f"Maior preço do dia: {info['highest_price']}")
        st.write(f"Preço ideal de compra: {info['buy_price']}")
        st.write(f"Preço ideal de venda: {info['sell_price']}")
        st.write("----")
