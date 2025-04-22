import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

st.set_page_config(layout="wide")
st.title("📈 TradeMaster AI – Assistente de Daytrade Cripto & Ações")

# Dicionários com as criptos e ações
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

stocks = {
    "Tesla (TSLA)": "tsla",
    "Amazon (AMZN)": "amzn",
    "Apple (AAPL)": "aapl",
    "Meta (META)": "meta",
    "Netflix (NFLX)": "nflx",
    "Nvidia (NVDA)": "nvda",
    "GameStop (GME)": "gme",
    "AMC Entertainment (AMC)": "amc",
    "Spotify (SPOT)": "spot",
    "Palantir (PLTR)": "pltr",
    "Roku (ROKU)": "roku",
    "Square (SQ)": "sq",
    "Zoom Video (ZM)": "zm",
    "DocuSign (DOCU)": "docu",
    "Beyond Meat (BYND)": "bynd",
    "Coinbase (COIN)": "coin",
    "Robinhood (HOOD)": "hood",
    "Moderna (MRNA)": "mrna",
    "Snowflake (SNOW)": "snow"
}

# -----------------------------
# FUNÇÃO PARA BUSCAR DADOS DA API
# -----------------------------

@st.cache_data(ttl=60)
def get_market_data(assets, asset_type="crypto"):
    if asset_type == "crypto":
        url = f"https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&ids={','.join(assets.values())}&order=market_cap_desc"
    else:  # stock data via another API
        url = f"https://api.twelvedata.com/time_series?symbol={','.join(assets.values())}&interval=1min&apikey=YOUR_TWELVE_DATA_API_KEY"
    
    r = requests.get(url)
    if r.status_code == 200:
        data = r.json()
        return pd.DataFrame([{
            "name": item.get("name", item.get("symbol")),
            "symbol": item.get("symbol").upper(),
            "volatility": abs(item.get("price_change_percentage_24h", 0) if asset_type == "crypto" else item.get("percent_change", 0)),
            "price": item.get("current_price", item["close"] if asset_type == "crypto" else 0),
            "low_24h": item.get("low_24h", item["low"] if asset_type == "crypto" else 0),
            "high_24h": item.get("high_24h", item["high"] if asset_type == "crypto" else 0),
            "buy_suggestion": round(item.get("current_price", 0) * 0.95, 4),
            "sell_suggestion": round(item.get("current_price", 0) * 1.05, 4)
        } for item in data])
    return pd.DataFrame()

# -----------------------------
# PAINEL DE VOLATILIDADE DAS CRIPTOS
# -----------------------------

st.subheader("📊 Volatilidade das Criptomoedas (últimas 24h)")

crypto_df = get_market_data(coins, asset_type="crypto")
crypto_df_sorted = crypto_df.sort_values("volatility", ascending=False)

fig_crypto_vol = go.Figure(go.Bar(
    x=crypto_df_sorted["volatility"],
    y=[f"{n} ({s})" for n, s in zip(crypto_df_sorted["name"], crypto_df_sorted["symbol"])],
    orientation='h',
    marker=dict(color='rgba(255,100,100,0.6)', line=dict(color='red', width=1.5))
))
fig_crypto_vol.update_layout(
    height=500,
    xaxis_title="Variação percentual (absoluta) nas últimas 24h",
    yaxis_title="Criptomoeda",
    title="🔺 Ranking de Volatilidade Atual (Criptos)",
    yaxis=dict(autorange="reversed")
)
st.plotly_chart(fig_crypto_vol, use_container_width=True)

# -----------------------------
# PAINEL DE VOLATILIDADE DAS AÇÕES
# -----------------------------

st.subheader("📊 Volatilidade das Ações (últimas 24h)")

stock_df = get_market_data(stocks, asset_type="stock")
stock_df_sorted = stock_df.sort_values("volatility", ascending=False)

fig_stock_vol = go.Figure(go.Bar(
    x=stock_df_sorted["volatility"],
    y=[f"{n} ({s})" for n, s in zip(stock_df_sorted["name"], stock_df_sorted["symbol"])],
    orientation='h',
    marker=dict(color='rgba(100,100,255,0.6)', line=dict(color='blue', width=1.5))
))
fig_stock_vol.update_layout(
    height=500,
    xaxis_title="Variação percentual (absoluta) nas últimas 24h",
    yaxis_title="Ação",
    title="🔺 Ranking de Volatilidade Atual (Ações)",
    yaxis=dict(autorange="reversed")
)
st.plotly_chart(fig_stock_vol, use_container_width=True)

# -----------------------------
# TABELA DE DETALHES DE CRIPTOS
# -----------------------------

st.markdown("### 🧾 Detalhes dos Ativos Cripto (Valores em USD)")
crypto_df_sorted["volatility"] = crypto_df_sorted["volatility"].map(lambda x: f"{x:.2f}%")
crypto_df_sorted["price"] = crypto_df_sorted["price"].map(lambda x: f"${x:.4f}")
crypto_df_sorted["low_24h"] = crypto_df_sorted["low_24h"].map(lambda x: f"${x:.4f}")
crypto_df_sorted["high_24h"] = crypto_df_sorted["high_24h"].map(lambda x: f"${x:.4f}")
crypto_df_sorted["buy_suggestion"] = crypto_df_sorted["buy_suggestion"].map(lambda x: f"${x:.4f}")
crypto_df_sorted["sell_suggestion"] = crypto_df_sorted["sell_suggestion"].map(lambda x: f"${x:.4f}")

st.dataframe(
    crypto_df_sorted[[
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
# TABELA DE DETALHES DE AÇÕES
# -----------------------------

st.markdown("### 🧾 Detalhes das Ações (Valores em USD)")
stock_df_sorted["volatility"] = stock_df_sorted["volatility"].map(lambda x: f"{x:.2f}%")
stock_df_sorted["price"] = stock_df_sorted["price"].map(lambda x: f"${x:.4f}")
stock_df_sorted["low_24h"] = stock_df_sorted["low_24h"].map(lambda x: f"${x:.4f}")
stock_df_sorted["high_24h"] = stock_df_sorted["high_24h"].map(lambda x: f"${x:.4f}")
stock_df_sorted["buy_suggestion"] = stock_df_sorted["buy_suggestion"].map(lambda x: f"${x:.4f}")
stock_df_sorted["sell_suggestion"] = stock_df_sorted["sell_suggestion"].map(lambda x: f"${x:.4f}")

st.dataframe(
    stock_df_sorted[[
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
