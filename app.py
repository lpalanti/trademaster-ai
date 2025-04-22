import requests
import pandas as pd
import streamlit as st
from streamlit_autorefresh import st_autorefresh

# --- Função para obter dados de criptomoedas ---
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
            'Ativo': item.get('name', '') + ' (' + item.get('symbol', '').upper() + ')',
            'Volatilidade': f"{item.get('price_change_percentage_24h', 0):.2f}%",
            'Preço Mínimo': f"${item.get('low_24h', 0):.2f}",
            'Preço Máximo': f"${item.get('high_24h', 0):.2f}",
            'Preço Ideal de Compra': f"${item.get('low_24h', 0):.2f}",
            'Preço Ideal de Venda': f"${item.get('high_24h', 0):.2f}",
        })

    return pd.DataFrame(ativos)

# --- Função para obter dados de ações ---
def obter_dados_acoes():
    API_KEY = 'IOKSXPMXJXFIKTI3'
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

        series = data['Time Series (1min)']
        times = list(series.keys())
        valores = [float(info['4. close']) for info in series.values()]
        preco_atual = float(series[times[0]]['4. close'])
        preco_minimo = min(valores)
        preco_maximo = max(valores)

        ativos.append({
            'Ativo': ticker,
            'Volatilidade': f"{((preco_maximo - preco_minimo) / preco_minimo) * 100:.2f}%",
            'Preço Mínimo': f"${preco_minimo:.2f}",
            'Preço Máximo': f"${preco_maximo:.2f}",
            'Preço Ideal de Compra': f"${preco_minimo:.2f}",
            'Preço Ideal de Venda': f"${preco_maximo:.2f}",
        })

    return pd.DataFrame(ativos)

# --- Função principal do app ---
def main():
    # Atualiza a cada 60 segundos (60000 ms)
    st_autorefresh(interval=60000, key="refresh")

    st.title("📊 Painel de Cripto e Ações")
    st.caption("Atualização automática a cada 60 segundos")

    st.subheader("💰 Criptomoedas")
    df_cripto = obter_dados_cripto()
    st.dataframe(df_cripto, use_container_width=True)

    st.subheader("📈 Ações")
    df_acoes = obter_dados_acoes()
    st.dataframe(df_acoes, use_container_width=True)

# --- Executa o app ---
if __name__ == "__main__":
    main()

