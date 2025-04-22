import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
import time
from datetime import datetime

st.set_page_config(page_title="TradeMaster AI", layout="wide")

st.title("📊 TradeMaster AI – Candlestick Cripto em Tempo Real")

# Inicializa variáveis de sessão
if "prices" not in st.session_state:
    st.session_state.prices = []

# Seleção de moeda
coin = st.selectbox("Escolha a Criptomoeda:", ["bitcoin", "ethereum", "solana", "dogecoin"])

# Função para pegar o preço atual
def get_price(coin):
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin}&vs_currencies=usd"
    r = requests.get(url)
    if r.status_code == 200:
        price = r.json()[coin]["usd"]
        return price
    return None

st.subheader("📊 Volatilidade das Criptomoedas (24h)")

@st.cache_data(ttl=60)
def get_volatility_data():
    ids = ",".join(coins.values())
    url = f"https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&ids={ids}&order=market_cap_desc"
    r = requests.get(url)
    if r.status_code == 200:
        data = r.json()
        return pd.DataFrame([{
            "name": item["name"],
            "symbol": item["symbol"].upper(),
            "volatility": abs(item["price_change_percentage_24h"] or 0)
        } for item in data])
    return pd.DataFrame()

vol_df = get_volatility_data()
vol_df_sorted = vol_df.sort_values("volatility", ascending=False)

fig_vol = go.Figure(go.Bar(
    x=vol_df_sorted["volatility"],
    y=[f"{n} ({s})" for n, s in zip(vol_df_sorted["name"], vol_df_sorted["symbol"])],
    orientation='h',
    marker=dict(color='rgba(255,100,100,0.6)', line=dict(color='red', width=1.5))
))

fig_vol.update_layout(
    height=500,
    xaxis_title="Variação percentual (absoluta) nas últimas 24h",
    yaxis_title="Criptomoeda",
    title="🔺 Ranking de Volatilidade Atual",
    yaxis=dict(autorange="reversed")
)

st.plotly_chart(fig_vol, use_container_width=True)


# Atualiza o histórico
price = get_price(coin)
if price:
    timestamp = datetime.now().strftime("%H:%M:%S")
    st.session_state.prices.append({"time": timestamp, "price": price})

# Converte histórico para DataFrame
df = pd.DataFrame(st.session_state.prices)

# Agrupa dados por minuto (OHLC simulado)
if len(df) >= 5:
    df["time_dt"] = pd.to_datetime(df["time"], format="%H:%M:%S")
    df.set_index("time_dt", inplace=True)
    ohlc = df["price"].resample("1T").ohlc().dropna()

    # Gráfico candlestick
    fig = go.Figure(data=[go.Candlestick(
        x=ohlc.index,
        open=ohlc["open"],
        high=ohlc["high"],
        low=ohlc["low"],
        close=ohlc["close"]
    )])
    fig.update_layout(title="Gráfico de Velas (Candlestick)", xaxis_title="Tempo", yaxis_title="Preço (USD)")
    st.plotly_chart(fig, use_container_width=True)

else:
    st.info("Aguardando dados suficientes para montar o gráfico de velas...")

# Exibe preço atual
st.metric(label=f"Preço Atual de {coin.capitalize()}", value=f"${price}")

# Aguarda e atualiza a cada 60 segundos
st.write("🔄 Atualizando a cada 60 segundos...")
time.sleep(60)
st.experimental_rerun()
