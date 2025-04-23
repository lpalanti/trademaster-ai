import streamlit as st
import pandas as pd
import requests
import yfinance as yf
from plotly import graph_objs as go

# Configuração do layout
st.set_page_config(layout="wide")
st.title("📊 TradeMaster AI - Painéis Integrados")

# Cotação USD/BRL
@st.cache_data(ttl=300)
def get_usd_brl():
    try:
        cotacao = yf.download("USDBRL=X", period="1d", interval="1m")
        return cotacao["Close"].iloc[-1]
    except:
        return 5.0

usd_brl = get_usd_brl()

# Cálculo de métricas
def calcular_metricas(df):
    if df.empty:
        return {}
    max_price = df["High"].max()
    min_price = df["Low"].min()
    vol = max_price - min_price
    vol_pct = (vol / min_price) * 100 if min_price != 0 else 0
    buy = min_price + 0.1 * vol
    sell = max_price - 0.1 * vol
    return {
        "Menor Preço do Dia": f"R$ {min_price:.2f}",
        "Maior Preço do Dia": f"R$ {max_price:.2f}",
        "Volatilidade": f"R$ {vol:.2f}",
        "% Volatilidade": f"{vol_pct:.2f}%",
        "Ideal Compra": f"R$ {buy:.2f}",
        "Ideal Venda": f"R$ {sell:.2f}",
    }

# Gráfico de candles
def plot_candle(df, nome):
    if df.empty:
        st.warning(f"Sem dados para {nome}.")
        return
    fig = go.Figure(data=[go.Candlestick(
        x=df.index,
        open=df['Open'],
        high=df['High'],
        low=df['Low'],
        close=df['Close']
    )])
    fig.update_layout(title=f"Gráfico de Candles - {nome}", height=300, xaxis_rangeslider_visible=False)
    st.plotly_chart(fig, use_container_width=True)

# Dados de Cripto com CoinGecko
def fetch_crypto(coin_id):
    try:
        url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/ohlc?vs_currency=usd&days=1"
        r = requests.get(url).json()
        df = pd.DataFrame(r, columns=["timestamp", "Open", "High", "Low", "Close"])
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
        df.set_index("timestamp", inplace=True)
        df[["Open", "High", "Low", "Close"]] *= usd_brl
        return df
    except:
        return pd.DataFrame()

# Dados com Yahoo Finance (ações e commodities)
def fetch_yahoo(ticker):
    try:
        df = yf.download(ticker, period="1d", interval="5m")
        df[["Open", "High", "Low", "Close"]] *= usd_brl
        return df
    except:
        return pd.DataFrame()

# ========== PAINEL CRIPTO ==========
st.header("💰 Criptomoedas")
cripto_ids = {
    "Bitcoin": "bitcoin", 
    "Ethereum": "ethereum", 
    "Solana": "solana"
}
dados_cripto = []

for nome, cid in cripto_ids.items():
    df = fetch_crypto(cid)
    metrics = calcular_metricas(df)
    metrics["Ativo"] = nome
    metrics["Fonte"] = "CoinGecko"
    dados_cripto.append(metrics)
    plot_candle(df, nome)

st.dataframe(pd.DataFrame(dados_cripto), use_container_width=True)

# ========== PAINEL AÇÕES ==========
st.header("📈 Ações")
acoes = ["AAPL", "TSLA", "AMZN"]
dados_acoes = []

for ticker in acoes:
    df = fetch_yahoo(ticker)
    metrics = calcular_metricas(df)
    metrics["Ativo"] = ticker
    metrics["Fonte"] = "Yahoo Finance"
    dados_acoes.append(metrics)
    plot_candle(df, ticker)

st.dataframe(pd.DataFrame(dados_acoes), use_container_width=True)

# ========== PAINEL COMMODITIES ==========
st.header("🛢️ Commodities")
commodities = {
    "Ouro": "GC=F",
    "Petróleo Brent": "BZ=F",
    "Café": "KC=F"
}
dados_commodities = []

for nome, ticker in commodities.items():
    df = fetch_yahoo(ticker)
    metrics = calcular_metricas(df)
    metrics["Ativo"] = nome
    metrics["Fonte"] = "Yahoo Finance"
    dados_commodities.append(metrics)
    plot_candle(df, nome)

st.dataframe(pd.DataFrame(dados_commodities), use_container_width=True)
