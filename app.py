import streamlit as st
import requests
import pandas as pd

API_KEY = 'IOKSXPMXJXFIKTI3'

# Ativos
CRYPTO = {
    "Bitcoin": "BTC",
    "Ethereum": "ETH",
    "Ripple": "XRP",
    "Dogecoin": "DOGE",
    "Litecoin": "LTC",
    "Cardano": "ADA",
    "Polkadot": "DOT",
    "Solana": "SOL",
    "Avalanche": "AVAX",
    "Chainlink": "LINK",
    "Shiba Inu": "SHIB",
    "Binance Coin": "BNB",
    "Polygon": "MATIC",
    "Uniswap": "UNI",
    "Terra": "LUNA"
}

STOCKS = {
    "Tesla": "TSLA",
    "Amazon": "AMZN",
    "Apple": "AAPL",
    "Meta": "META",
    "Netflix": "NFLX",
    "Nvidia": "NVDA",
    "GameStop": "GME",
    "AMC Entertainment": "AMC",
    "Spotify": "SPOT",
    "Palantir": "PLTR",
    "Roku": "ROKU",
    "Square": "SQ",
    "Zoom Video": "ZM",
    "DocuSign": "DOCU",
    "Beyond Meat": "BYND",
    "Coinbase": "COIN",
    "Robinhood": "HOOD",
    "Moderna": "MRNA",
    "Snowflake": "SNOW"
}

COMMODITIES = {
    "Ouro": "XAUUSD",
    "Petróleo Brent": "BZ",
    "Petróleo WTI": "CL",
    "Cobre": "HG",
    "Algodão": "CT",
    "Café": "KC",
    "Soja": "ZS",
    "Milho": "ZC",
    "Açúcar": "SB",
    "Paládio": "PA"
}


@st.cache_data(ttl=180)
def get_usd_brl():
    url = f"https://www.alphavantage.co/query?function=CURRENCY_EXCHANGE_RATE&from_currency=USD&to_currency=BRL&apikey={API_KEY}"
    response = requests.get(url).json()
    try:
        rate = float(response['Realtime Currency Exchange Rate']['5. Exchange Rate'])
    except:
        rate = 5.0  # fallback
    return rate


@st.cache_data(ttl=180)
def fetch_data(symbol, market="stock", usd_brl=5.0):
    if market == "crypto":
        url = f"https://www.alphavantage.co/query?function=DIGITAL_CURRENCY_INTRADAY&symbol={symbol}&market=USD&apikey={API_KEY}"
    else:
        url = f"https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={symbol}&interval=5min&apikey={API_KEY}"

    response = requests.get(url)
    data = response.json()

    try:
        if market == "crypto":
            ts = data["Time Series (Digital Currency Intraday)"]
        else:
            ts = data["Time Series (5min)"]

        df = pd.DataFrame(ts).T.astype(float)
        high = df["2. high"].max()
        low = df["3. low"].min()

        # Conversão para reais
        high *= usd_brl
        low *= usd_brl
        volatility = high - low
        volatility_pct = (volatility / low) * 100
        ideal_buy = low + volatility * 0.1
        ideal_sell = high - volatility * 0.1

        return {
            "Volatilidade": f"R$ {volatility:.2f}",
            "% Volatilidade": f"{volatility_pct:.2f}%",
            "Menor Preço do Dia": f"R$ {low:.2f}",
            "Maior Preço do Dia": f"R$ {high:.2f}",
            "Ideal Compra": f"R$ {ideal_buy:.2f}",
            "Ideal Venda": f"R$ {ideal_sell:.2f}"
        }
    except:
        return {
            "Volatilidade": "-",
            "% Volatilidade": "-",
            "Menor Preço do Dia": "-",
            "Maior Preço do Dia": "-",
            "Ideal Compra": "-",
            "Ideal Venda": "-"
        }


def render_category(name, data_dict, market_type, usd_brl):
    st.subheader(name)
    rows = []
    for label, symbol in data_dict.items():
        data = fetch_data(symbol, market_type, usd_brl)
        row = {"Ativo": label}
        row.update(data)
        rows.append(row)
    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True)


# Layout
st.set_page_config(page_title="TradeMaster AI", layout="wide")
st.title("📊 TradeMaster AI — Painel em Reais (R$) Atualizado a cada 3 minutos")

usd_brl = get_usd_brl()
col1, col2, col3 = st.columns(3)

with col1:
    render_category("💰 Cripto", CRYPTO, "crypto", usd_brl)

with col2:
    render_category("📈 Ações", STOCKS, "stock", usd_brl)

with col3:
    render_category("🛢️ Commodities", COMMODITIES, "stock", usd_brl)
