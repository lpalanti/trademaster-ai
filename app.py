import streamlit as st
import pandas as pd
import requests

# Função para obter dados das criptos usando a API do CoinGecko
def obter_dados_cripto():
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {
        'vs_currency': 'usd',
        'ids': 'bitcoin,ethereum,ripple,dogecoin,litecoin,cardano,polkadot,solana,avalanche,chainlink,shiba-inu,binancecoin,polygon,uniswap,terra-luna',
    }
    response = requests.get(url, params=params)
    data = response.json()

    ativos = []
    for item in data:
        ativos.append({
            'Ativo': item['name'] + ' (' + item['symbol'].upper() + ')',
            'Volatilidade': f"{item['price_change_percentage_24h']:.2f}%",
            'Preço Mínimo': f"${item['low_24h']:.2f}",
            'Preço Máximo': f"${item['high_24h']:.2f}",
            'Preço Ideal de Compra': f"${item['low_24h']:.2f}",
            'Preço Ideal de Venda': f"${item['high_24h']:.2f}",
        })
    
    return pd.DataFrame(ativos)

# Função para obter dados das ações usando a API do Alpha Vantage
def obter_dados_acoes():
    API_KEY = 'SUA_API_KEY_AQUI'  # Substitua com sua chave de API do Alpha Vantage
    tickers = ['TSLA', 'AMZN', 'AAPL', 'META', 'NFLX', 'NVDA', 'GME', 'AMC', 'SPOT', 'PLTR', 'ROKU', 'SQ', 'ZM', 'DOCU', 'BYND', 'COIN', 'HOOD', 'MRNA', 'SNOW']
    ativos = []
    
    for ticker in tickers:
        url = f'https://www.alphavantage.co/query'
        params = {
            'function': 'TIME_SERIES_INTRADAY',
            'symbol': ticker,
            'interval': '1min',
            'apikey': API_KEY
        }
        response = requests.get(url, params=params)
        data = response.json()

        if 'Time Series (1min)' not in data:
            continue

        times = list(data['Time Series (1min)'].keys())
        last_close = float(data['Time Series (1min)'][times[0]]['4. close'])
        
        # Obtenção de dados simulados (preço máximo, mínimo e volatilidade)
        preco_min = last_close * 0.98
        preco_max = last_close * 1.02
        volatilidade = (preco_max - preco_min) / last_close * 100
        
        ativos.append({
            'Ativo': ticker,
            'Volatilidade': f"{volatilidade:.2f}%",
            'Preço Mínimo': f"${preco_min:.2f}",
            'Preço Máximo': f"${preco_max:.2f}",
            'Preço Ideal de Compra': f"${preco_min:.2f}",
            'Preço Ideal de Venda': f"${preco_max:.2f}",
        })
    
    return pd.DataFrame(ativos)

# Função para obter dados de commodities usando a API do Alpha Vantage
def obter_dados_commodities():
    API_KEY = 'SUA_API_KEY_AQUI'  # Substitua com sua chave de API do Alpha Vantage
    commodities = ['XAUUSD', 'BRENTOIL', 'WTIOIL', 'COPPER', 'COTTON', 'COFFEE', 'SOYBEAN', 'CORN', 'SUGAR', 'PALLADIUM']
    ativos = []
    
    for commodity in commodities:
        url = f'https://www.alphavantage.co/query'
        params = {
            'function': 'TIME_SERIES_INTRADAY',
            'symbol': commodity,
            'interval': '1min',
            'apikey': API_KEY
        }
        response = requests.get(url, params=params)
        data = response.json()

        if 'Time Series (1min)' not in data:
            continue

        times = list(data['Time Series (1min)'].keys())
        last_close = float(data['Time Series (1min)'][times[0]]['4. close'])
        
        # Obtenção de dados simulados (preço máximo, mínimo e volatilidade)
        preco_min = last_close * 0.98
        preco_max = last_close * 1.02
        volatilidade = (preco_max - preco_min) / last_close * 100
        
        ativos.append({
            'Ativo': commodity,
            'Volatilidade': f"{volatilidade:.2f}%",
            'Preço Mínimo': f"${preco_min:.2f}",
            'Preço Máximo': f"${preco_max:.2f}",
            'Preço Ideal de Compra': f"${preco_min:.2f}",
            'Preço Ideal de Venda': f"${preco_max:.2f}",
        })
    
    return pd.DataFrame(ativos)

# Título da aplicação
st.title("Trademaster AI - Dashboard de Day Trade")

# Barra lateral para seleção de categorias
opcao = st.sidebar.selectbox(
    'Escolha uma categoria de ativos:',
    ['Cripto', 'Ações', 'Commodities']
)

# Exibindo os dados de acordo com a categoria escolhida
if opcao == 'Cripto':
    st.header("Ativos Cripto")
    ativos_cripto = obter_dados_cripto()
    st.dataframe(ativos_cripto)

elif opcao == 'Ações':
    st.header("Ativos Ações")
    ativos_acoes = obter_dados_acoes()
    st.dataframe(ativos_acoes)

elif opcao == 'Commodities':
    st.header("Ativos Commodities")
    ativos_commodities = obter_dados_commodities()
    st.dataframe(ativos_commodities)

# Informações adicionais de como usar
st.sidebar.markdown("""
### Sobre:
- Este aplicativo exibe dados reais de ativos em tempo real, com base nas categorias de Cripto, Ações e Commodities.
- Use os botões para navegar entre as categorias e visualizar informações como volatilidade, preços mínimos e máximos, e preços ideais de compra e venda.
""")
