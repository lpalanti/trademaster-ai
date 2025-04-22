import streamlit as st
from streamlit_autorefresh import st_autorefresh
import pandas as pd
import requests
import time

st.set_page_config(page_title="TradeMaster AI", layout="wide")

# Autorefresh a cada 10 segundos
st_autorefresh(interval=10 * 1000, key="datarefresh")

st.title("📈 TradeMaster AI")
st.markdown("### Análise em tempo real de ações e criptomoedas")

with st.sidebar:
    st.header("Configurações")
    ativo = st.text_input("Ticker do ativo", value="BTC-USD")
    intervalo = st.selectbox("Intervalo", options=["1m", "5m", "15m", "1h", "1d"], index=4)
    st.caption("Atualizando automaticamente a cada 10 segundos.")

@st.cache_data(ttl=10)
def obter_dados(ticker, intervalo):
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?interval={intervalo}&range=1d"
    resposta = requests.get(url)
    if resposta.status_code != 200:
        return None
    dados = resposta.json()
    try:
        timestamps = dados["chart"]["result"][0]["timestamp"]
        precos = dados["chart"]["result"][0]["indicators"]["quote"][0]["close"]
        df = pd.DataFrame({
            "Tempo": pd.to_datetime(timestamps, unit="s"),
            "Preço": precos
        }).dropna()
        return df
    except Exception as e:
        return None

dados = obter_dados(ativo, intervalo)

if dados is None or dados.empty:
    st.error("Erro ao carregar dados. Verifique o ticker ou tente novamente.")
else:
    st.line_chart(dados.set_index("Tempo"))

