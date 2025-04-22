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

    # Adicionando cálculo de preço ideal de compra e venda com 5% de margem
    for item in data:
        item['buy_price'] = item['current_price'] * 0.95  # 5% de desconto para compra
        item['sell_price'] = item['current_price'] * 1.05  # 5% de aumento para venda

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
            "buy_price": hist['Close'].iloc[0] * 0.95,  # 5% de desconto para compra
            "sell_price": hist['Close'].iloc[0] * 1.05  # 5% de aumento para venda
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
            "buy_price": hist['Close'].iloc[0] * 0.95,  # 5% de desconto para compra
            "sell_price": hist['Close'].iloc[0] * 1.05  # 5% de aumento para venda
        }
    return data

# Página Inicial
st.title('Day Trade Dashboard')

# Obtenção dos dados
cripto_data = get_cripto_data()
stock_data = get_stock_data()
commodities_data = get_commodities_data()

# Tabela de Criptoativos
st.subheader("Criptoativos")
cripto_df = cripto_data[['name', 'current_price', 'price_change_percentage_24h', 'low_24h', 'high_24h', 'buy_price', 'sell_price']]
cripto_df = cripto_df.rename(columns={
    'name': 'Ativo',
    'current_price': 'Preço Atual (USD)',
    'price_change_percentage_24h': 'Volatilidade (%)',
    'low_24h': 'Menor Preço do Dia (USD)',
    'high_24h': 'Maior Preço do Dia (USD)',
    'buy_price': 'Preço Ideal de Compra (USD)',
    'sell_price': 'Preço Ideal de Venda (USD)'
})
st.dataframe(cripto_df)

# Tabela de Ações
st.subheader("Ações")
stock_df = pd.DataFrame(stock_data).T
stock_df = stock_df.rename(columns={
    'volatility': 'Volatilidade (%)',
    'lowest_price': 'Menor Preço do Dia (USD)',
    'highest_price': 'Maior Preço do Dia (USD)',
    'buy_price': 'Preço Ideal de Compra (USD)',
    'sell_price': 'Preço Ideal de Venda (USD)'
})
stock_df['Ativo'] = stock_df.index
stock_df = stock_df[['Ativo', 'Volatilidade (%)', 'Menor Preço do Dia (USD)', 'Maior Preço do Dia (USD)', 'Preço Ideal de Compra (USD)', 'Preço Ideal de Venda (USD)']]
st.dataframe(stock_df)

# Tabela de Commodities
st.subheader("Commodities")
commodities_df = pd.DataFrame(commodities_data).T
commodities_df = commodities_df.rename(columns={
    'volatility': 'Volatilidade (%)',
    'lowest_price': 'Menor Preço do Dia (USD)',
    'highest_price': 'Maior Preço do Dia (USD)',
    'buy_price': 'Preço Ideal de Compra (USD)',
    'sell_price': 'Preço Ideal de Venda (USD)'
})
commodities_df['Ativo'] = commodities_df.index
commodities_df = commodities_df[['Ativo', 'Volatilidade (%)', 'Menor Preço do Dia (USD)', 'Maior Preço do Dia (USD)', 'Preço Ideal de Compra (USD)', 'Preço Ideal de Venda (USD)']]
st.dataframe(commodities_df)
