import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

st.set_page_config(layout="wide")
st.title("📈 TradeMaster AI – Assistente de Daytrade Cripto")

# Dicionário com os ativos
coins = {
    "Bitcoin (BTC)": "bitcoin",
    "Ethereum (ETH)": "ethereum",
    "Ripple (XRP)": "ripple",
    "Dogecoin (DOGE)": "dogecoin",
    "Litecoin (LTC)": "litecoin",
    "Cardano (ADA)": "cardano",
    "Polkadot (DOT)": "polkadot",
    "Solana (SOL)": "solana",
    "Avalanche (AVAX)": "avalanche-2",
    "Chainlink (LINK)": "chainlink",
    "Shiba Inu (SHIB)": "shiba-inu",
    "Binance Coin (BNB)": "binancecoin",
    "Polygon (MATIC)": "polygon",
    "Uniswap (UNI)": "uniswap",
    "Terra (LUNA)": "terra-luna"
}

# -----------------------------
# VOLATILIDADE
# -----------------------------

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
            "volatility": abs(item["price_change_percentage_24h"] or 0),
            "price": item["current_price"],
            "low_24h": item["low_24h"],
            "high_24h": item["high_24h"],
            "buy_suggestion": round(item["current_price"] * 0.95, 4),
            "sell_suggestion": round(item["current_price"] * 1.05, 4)
        } for item in data])
    return pd.DataFrame()

st.subheader("📊 Volatilidade das Criptomoedas (últimas 24h)")

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

# -----------------------------
# TABELA DETALHADA
# -----------------------------

st.markdown("### 🧾 Detalhes dos Ativos (Valores em USD)")
vol_df_sorted["volatility"] = vol_df_sorted["volatility"].map(lambda x: f"{x:.2f}%")
vol_df_sorted["price"] = vol_df_sorted["price"].map(lambda x: f"${x:.4f}")
vol_df_sorted["low_24h"] = vol_df_sorted["low_24h"].map(lambda x: f"${x:.4f}")
vol_df_sorted["high_24h"] = vol_df_sorted["high_24h"].map(lambda x: f"${x:.4f}")
vol_df_sorted["buy_suggestion"] = vol_df_sorted["buy_suggestion"].map(lambda x: f"${x:.4f}")
vol_df_sorted["sell_suggestion"] = vol_df_sorted["sell_suggestion"].map(lambda x: f"${x:.4f}")

st.dataframe(
    vol_df_sorted[[
        "name", "symbol", "volatility", "price",
        "low_24h", "high_24h", "buy_suggestion", "sell_suggestion"
    ]].rename(columns={
        "name": "Nome",
        "symbol": "Ticker",
        "volatility": "Volatilidade (24h)",
        "price": "Preço atual",
        "low_24h": "Mín. do dia",
        "high_24h": "Máx. do dia",
        "buy_suggestion": "Sugestão de Compra",
        "sell_suggestion": "Sugestão de Venda"
    }),
    use_container_width=True,
    height=500
)

# -----------------------------
# ATIVO SELECIONADO
# -----------------------------

st.subheader("📉 Análise do Ativo Selecionado")

selected_coin = st.selectbox("Escolha a criptomoeda", list(coins.keys()))
coin_id = coins[selected_coin]

@st.cache_data(ttl=60)
def get_coin_data(coin_id):
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart?vs_currency=usd&days=1&interval=minute"
    r = requests.get(url)
    if r.status_code == 200:
        data = r.json()
        return data
    return None

data = get_coin_data(coin_id)

if data and "prices" in data:
    df = pd.DataFrame(data["prices"], columns=["timestamp", "price"])
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit='ms')
    df["datetime"] = df["timestamp"].dt.strftime("%H:%M")

    # Gerar candles (OHLC por minuto)
    ohlc = df.set_index("timestamp").resample("1min").agg({
        "price": ["first", "max", "min", "last"]
    }).dropna()
    ohlc.columns = ["open", "high", "low", "close"]
    ohlc.reset_index(inplace=True)

    fig = go.Figure(data=[go.Candlestick(
        x=ohlc["timestamp"],
        open=ohlc["open"],
        high=ohlc["high"],
        low=ohlc["low"],
        close=ohlc["close"],
        name=selected_coin
    )])
    fig.update_layout(
        title=f"📅 Gráfico Candle - {selected_coin}",
        xaxis_title="Horário",
        yaxis_title="Preço (USD)",
        xaxis_rangeslider_visible=False,
        height=600
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.error("Erro ao carregar os dados da criptomoeda.")
