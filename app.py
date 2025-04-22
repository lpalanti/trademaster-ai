import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import pytz
from time import sleep

st.set_page_config(page_title="TradeMaster AI", layout="wide")

st.title("📈 TradeMaster AI – Sugeridor de Ativos Inteligente")
st.markdown("**Análise com base nas últimas 3 horas e desempenho do dia**")

# Lista de 50 ativos populares 🇧🇷🇺🇸
tickers = [
    # BR
    "PETR4.SA", "VALE3.SA", "ITUB4.SA", "BBDC4.SA", "BBAS3.SA",
    "MGLU3.SA", "WEGE3.SA", "RENT3.SA", "B3SA3.SA", "LREN3.SA",
    "ABEV3.SA", "RADL3.SA", "JBSS3.SA", "RAIL3.SA", "GGBR4.SA",
    "BRFS3.SA", "ELET3.SA", "EMBR3.SA", "CSNA3.SA", "CYRE3.SA",
    "UGPA3.SA", "CCRO3.SA", "CMIG4.SA", "ENBR3.SA", "HAPV3.SA",
    # EUA
    "AAPL", "MSFT", "GOOGL", "AMZN", "TSLA",
    "META", "NVDA", "NFLX", "INTC", "AMD",
    "BAC", "JPM", "WMT", "DIS", "PEP",
    "NKE", "T", "KO", "PFE", "BA",
    "C", "XOM", "CVX", "MRNA", "ADBE"
]

# Timezone correto
br_tz = pytz.timezone('America/Sao_Paulo')
agora = datetime.now(br_tz)
inicio = agora - timedelta(hours=3)

@st.cache_data(ttl=300)
def analisar_ativo(ticker):
    try:
        dados = yf.download(ticker, interval="5m", period="1d", progress=False)

        if dados.empty:
            return None

        dados = dados.dropna()
        dados_3h = dados[dados.index >= inicio]

        if dados_3h.empty:
            return None

        preco_atual = dados_3h["Close"][-1]
        preco_inicio = dados_3h["Close"][0]
        variacao = ((preco_atual - preco_inicio) / preco_inicio) * 100

        melhor_compra = dados_3h["Low"].min()
        melhor_venda = dados_3h["High"].max()

        return {
            "Ativo": ticker,
            "Preço Atual": round(preco_atual, 2),
            "Variação (%)": round(variacao, 2),
            "Melhor Compra": round(melhor_compra, 2),
            "Melhor Venda": round(melhor_venda, 2)
        }

    except Exception as e:
        return None

# 🔄 Análise com barra de progresso
st.info("Analisando ativos, isso pode levar alguns segundos...")
analises = []
with st.spinner("🔍 Coletando dados..."):
    for i, ticker in enumerate(tickers):
        resultado = analisar_ativo(ticker)
        if resultado:
            analises.append(resultado)
        st.progress((i + 1) / len(tickers))
        sleep(0.05)

# ✅ Resultados
if analises:
    df_resultado = pd.DataFrame(analises)
    df_validos = df_resultado[df_resultado['Variação (%)'].notnull()]
    top10 = df_validos.sort_values("Variação (%)", ascending=False).head(10)

    st.success("✅ Top 10 ativos com melhor desempenho nas últimas 3 horas:")
    st.dataframe(top10.reset_index(drop=True), use_container_width=True)
else:
    st.error("Nenhum dado disponível no momento. Tente novamente mais tarde.")

