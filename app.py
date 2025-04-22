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

    try:
        response = requests.get(url, params=params)
        data = response.json()

        ativos = []
        for item in data:
            if all(k in item for k in ['name', 'symbol', 'price_change_percentage_24h', 'low_24h', 'high_24h']):
                ativos.append({
                    'Ativo': f"{item['name']} ({item['symbol'].upper()})",
                    'Volatilidade': f"{item['price_change_percentage_24h']:.2f}%",
                    'Preço Mínimo': f"${item['low_24h']:.2f}",
                    'Preço Máximo': f"${item['high_24h']:.2f}",
                    'Preço Ideal de Compra': f"${item['low_24h']:.2f}",
                    'Preço Ideal de Venda': f"${item['high_24h']:.2f}",
                })

        return pd.DataFrame(ativos)

    except Exception as e:
        st.error(f"Erro ao obter dados das criptomoedas: {e}")
        return pd.DataFrame()

# Função para obter dados das ações usando a API do Alpha Vantage
def obter_dados_acoes():
    API_KEY = 'IOKSXPMXJXFIKTI3'
    tickers = ['TSLA', 'AMZN', 'AAPL', 'META', 'NFLX', 'NVDA']
    ativos = []

    for ticker in tickers:
        try:
            url = 'https://www.alphavantage.co/query'
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
            latest_data = data['Time Series (1min)'][times[0]]

            ativo = {
                'Ativo': ticker,
                'Volatilidade': "N/A",
                'Preço Mínimo': f"${float(latest_data['3. low']):.2f}",
                'Preço Máximo': f"${float(latest_data['2. high']):.2f}",
                'Preço Ideal de Compra': f"${float(latest_data['3. low']):.2f}",
                'Preço Ideal de Venda': f"${float(latest_data['2. high']):.2f}",
            }
            ativos.append(ativo)

        except Exception as e:
            st.error(f"Erro ao obter dados da ação {ticker}: {e}")
            continue

    return pd.DataFrame(ativos)

# Função principal do app
def main():
    st.title("Painel de Cripto e Ações - Atualização a cada 1 minuto")

    df_cripto = obter_dados_cripto()
    st.header("Criptomoedas")
    st.dataframe(df_cripto)

    df_acoes = obter_dados_acoes()
    st.header("Ações")
    st.dataframe(df_acoes)

    # Atualização automática a cada minuto
    st.caption("Atualizando a cada 60 segundos...")
    time.sleep(60)
    st.experimental_rerun()

if __name__ == "__main__":
    main()
