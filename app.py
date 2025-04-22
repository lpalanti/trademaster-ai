import streamlit as st
import requests
import pandas as pd
import time

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
    API_KEY = 'IOKSXPMXJXFIKTI3'  # Chave da API do Alpha Vantage
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
        ativo = {
            'Ativo': ticker,
            'Volatilidade': f"N/A",  # Ações não possuem volatilidade em 24h como as criptos
            'Preço Mínimo': f"${float(data['Time Series (1min)'][times[0]]['3. low']):.2f}",
            'Preço Máximo': f"${float(data['Time Series (1min)'][times[0]]['2. high']):.2f}",
            'Preço Ideal de Compra': f"${float(data['Time Series (1min)'][times[0]]['3. low']):.2f}",
            'Preço Ideal de Venda': f"${float(data['Time Series (1min)'][times[0]]['2. high']):.2f}",
        }
        ativos.append(ativo)

    return pd.DataFrame(ativos)

# Função principal do app
def main():
    # Definindo título
    st.title("Monitor de Criptomoedas e Ações")

    # Exibir dados de criptomoedas
    st.header("Dados de Criptomoedas")
    df_cripto = obter_dados_cripto()
    st.write(df_cripto)

    # Exibir dados de ações
    st.header("Dados de Ações")
    df_acoes = obter_dados_acoes()
    st.write(df_acoes)

    # Atualização automática a cada 1 minuto
    while True:
        time.sleep(60)  # Espera 60 segundos
        st.experimental_rerun()  # Atualiza a página

# Verifica se o arquivo está sendo executado diretamente e chama a função main
if __name__ == "__main__":
    main()
