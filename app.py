import requests
import pandas as pd
import streamlit as st

# Função para obter dados das criptos usando a API do CoinGecko
def obter_dados_cripto():
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {
        'vs_currency': 'usd',
        'ids': 'bitcoin,ethereum,ripple,dogecoin,litecoin,cardano,polkadot,solana,avalanche,chainlink,shiba-inu,binancecoin,polygon,uniswap,terra-luna',
    }
    response = requests.get(url, params=params)

    # Verificar se a requisição foi bem-sucedida
    if response.status_code != 200:
        st.error("Erro ao obter dados da API de criptos")
        return pd.DataFrame()

    data = response.json()

    # Verificar se os dados retornados são válidos
    if not isinstance(data, list):
        st.error("Erro: Dados retornados não são uma lista.")
        return pd.DataFrame()

    ativos = []
    for item in data:
        try:
            ativos.append({
                'Ativo': item['name'] + ' (' + item['symbol'].upper() + ')',
                'Volatilidade': f"{item['price_change_percentage_24h']:.2f}%",
                'Preço Mínimo': f"${item['low_24h']:.2f}",
                'Preço Máximo': f"${item['high_24h']:.2f}",
                'Preço Ideal de Compra': f"${item['low_24h']:.2f}",
                'Preço Ideal de Venda': f"${item['high_24h']:.2f}",
            })
        except KeyError as e:
            st.warning(f"Erro ao processar dados para o ativo: {item.get('name', 'desconhecido')}. Chave faltando: {e}")
            continue
    
    # Retorna o DataFrame com os dados
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

        # Verificar se a requisição foi bem-sucedida
        if response.status_code != 200:
            st.warning(f"Erro ao obter dados da ação: {ticker}")
            continue
        
        data = response.json()

        # Verificar se os dados retornados são válidos
        if 'Time Series (1min)' not in data:
            st.warning(f"Ação {ticker}: Dados não encontrados.")
            continue

        times = list(data['Time Series (1min)'].keys())
        last_close = float(data['Time Series (1min)'][times[0]]['4. close'])

        ativos.append({
            'Ativo': ticker,
            'Último Preço': f"${last_close:.2f}",
            'Data': times[0],
        })

    return pd.DataFrame(ativos)
