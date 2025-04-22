import streamlit as st
import pandas as pd
import requests
import yfinance as yf
from datetime import datetime

st.set_page_config(page_title="Painel Day Trade", layout="wide")
st.title("📊 Painel de Day Trade - Cripto, Ações e Commodities")
st.caption("Atualização manual ou a cada 3 minutos via cache.")

# Sidebar de navegação
opcao = st.sidebar.radio("Selecione o Painel:", ["Cripto", "Ações", "Commodities"])

# CRIPTO: via CoinGecko
def obter_dados_cripto():
    ids = "bitcoin,ethereum,ripple,dogecoin,litecoin,cardano,polkadot,solana,avalanche,chainlink,shiba-inu,binancecoin,polygon,uniswap,terra-luna"
    url = f"https://api.coingecko.com/api/v3/coins/markets"
    params = {
        "vs_currency": "usd",
        "ids": ids,
    }
    r = requests.get(url, params=params)
    data = r.json()

    rows = []
    for c in data:
        vol = round(c['high_24h'] - c['low_24h'], 2)
        pct = round((vol / c['low_24h']) * 100, 2) if c['low_24h'] else 0
        rows.append({
            "Ativo": f"{c['name']} ({c['symbol'].upper()})",
            "Volatilidade": vol,
            "% Volatilidade": f"{pct}%",
            "Menor Preço": f"${c['low_24h']:.2f}",
            "Maior Preço": f"${c['high_24h']:.2f}",
            "Preço Ideal de Compra": f"${c['low_24h']:.2f}",
            "Preço Ideal de Venda": f"${c['high_24h']:.2f}"
        })

    return pd.DataFrame(rows)

# AÇÕES: via Alpha Vantage
def obter_dados_acoes():
    API_KEY = "IOKSXPMXJXFIKTI3"
    tickers = ['TSLA', 'AMZN', 'AAPL', 'META', 'NFLX', 'NVDA', 'GME', 'AMC', 'SPOT', 'PLTR', 'ROKU', 'SQ', 'ZM', 'DOCU', 'BYND', 'COIN', 'HOOD', 'MRNA', 'SNOW']
    resultados = []

    for t in tickers:
        url = "https://www.alphavantage.co/query"
        params = {
            "function": "TIME_SERIES_DAILY",
            "symbol": t,
            "apikey": API_KEY
        }
        r = requests.get(url, params=params)
        data = r.json()

        try:
            series = data["Time Series (Daily)"]
            ultimos = list(series.values())[:2]
            atual = ultimos[0]
            anterior = ultimos[1]

            minimo = float(atual["3. low"])
            maximo = float(atual["2. high"])
            vol = round(maximo - minimo, 2)
            pct = round((vol / minimo) * 100, 2) if minimo else 0

            resultados.append({
                "Ativo": t,
                "Volatilidade": vol,
                "% Volatilidade": f"{pct}%",
                "Menor Preço": f"${minimo:.2f}",
                "Maior Preço": f"${maximo:.2f}",
                "Preço Ideal de Compra": f"${minimo:.2f}",
                "Preço Ideal de Venda": f"${maximo:.2f}",
            })
        except:
            continue

    return pd.DataFrame(resultados)

# COMMODITIES: via yfinance
def obter_dados_commodities():
    ativos = {
        "Ouro": "XAUUSD=X",
        "Brent": "BZ=F",
        "WTI": "CL=F",
        "Cobre": "HG=F",
        "Algodão": "CT=F",
        "Café": "KC=F",
        "Soja": "ZS=F",
        "Milho": "ZC=F",
        "Açúcar": "SB=F",
        "Paládio": "PA=F",
    }

    resultados = []

    for nome, ticker in ativos.items():
        try:
            df = yf.download(ticker, period="1d", interval="1h", progress=False)
            if df.empty:
                continue
            minimo = df["Low"].min()
            maximo = df["High"].max()
            vol = round(maximo - minimo, 2)
            pct = round((vol / minimo) * 100, 2) if minimo else 0

            resultados.append({
                "Ativo": nome,
                "Volatilidade": vol,
                "% Volatilidade": f"{pct}%",
                "Menor Preço": f"${minimo:.2f}",
                "Maior Preço": f"${maximo:.2f}",
                "Preço Ideal de Compra": f"${minimo:.2f}",
                "Preço Ideal de Venda": f"${maximo:.2f}",
            })
        except:
            continue

    return pd.DataFrame(resultados)

# Mostra o painel certo
if opcao == "Cripto":
    st.subheader("🪙 Criptomoedas")
    df = obter_dados_cripto()
    st.dataframe(df, use_container_width=True)

elif opcao == "Ações":
    st.subheader("📈 Ações")
    df = obter_dados_acoes()
    st.dataframe(df, use_container_width=True)

elif opcao == "Commodities":
    st.subheader("🌾 Commodities")
    df = obter_dados_commodities()
    st.dataframe(df, use_container_width=True)

# Rodapé
st.caption(f"Atualizado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
