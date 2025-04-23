# app.py

import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objs as go
from datetime import datetime, timedelta

st.set_page_config(layout="wide")
st.title("📈 Painel de Ações - TradeMaster AI")

TICKERS = [
    "PETR4.SA", "VALE3.SA", "ITUB4.SA", "BBDC4.SA", "ABEV3.SA",
    "WEGE3.SA", "MGLU3.SA", "B3SA3.SA", "BBAS3.SA", "GGBR4.SA",
    "RENT3.SA", "LREN3.SA", "JBSS3.SA", "ELET3.SA", "CSNA3.SA",
    "HAPV3.SA", "PRIO3.SA", "SUZB3.SA", "RADL3.SA", "ASAI3.SA"
]

PERIOD_OPTIONS = {
    "1 Dia": "1d", "5 Dias": "5d", "1 Mês": "1mo", "3 Meses": "3mo",
    "6 Meses": "6mo", "1 Ano": "1y", "2 Anos": "2y", "5 Anos": "5y", 
    "Ano até agora": "ytd", "Máximo": "max"
}

@st.cache_data(ttl=180)
def get_stock_data():
    data = []
    for ticker in TICKERS:
        try:
            df = yf.download(ticker, period="1d", interval="1m", progress=False)
            if not df.empty:
                open_price = df['Open'].iloc[0]
                close_price = df['Close'].iloc[-1]
                high_price = df['High'].max()
                low_price = df['Low'].min()
                change = ((close_price - open_price) / open_price) * 100

                data.append({
                    "Ticker": ticker,
                    "Preço": round(close_price, 2),
                    "Abertura": round(open_price, 2),
                    "Máxima": round(high_price, 2),
                    "Mínima": round(low_price, 2),
                    "Variação (%)": round(change, 2),
                })
        except Exception as e:
            st.warning(f"Erro ao buscar dados para {ticker}: {e}")
    return pd.DataFrame(data)

def plot_candlestick(ticker, period):
    df = yf.download(ticker, period=period, interval="1d", progress=False)
    if df.empty:
        st.error("Sem dados disponíveis para este período.")
        return
    fig = go.Figure(data=[go.Candlestick(
        x=df.index,
        open=df['Open'],
        high=df['High'],
        low=df['Low'],
        close=df['Close'],
        name=ticker
    )])
    fig.update_layout(title=f"Gráfico de Candlestick - {ticker}", xaxis_title="Data", yaxis_title="Preço")
    st.plotly_chart(fig, use_container_width=True)

def main():
    st.subheader("Painel de Ações em Tempo Real")
    df = get_stock_data()

    if df.empty:
        st.error("Nenhum dado encontrado.")
        return

    sort_by = st.selectbox("Ordenar por", df.columns, index=0)
    df = df.sort_values(by=sort_by, ascending=False)

    st.dataframe(df, use_container_width=True)

    st.markdown("---")
    st.subheader("📊 Visualizar Gráfico")

    selected_ticker = st.selectbox("Escolha o ativo para visualizar o gráfico", df["Ticker"].tolist())
    selected_period = st.selectbox("Período", list(PERIOD_OPTIONS.keys()), index=1)
    period_code = PERIOD_OPTIONS[selected_period]

    plot_candlestick(selected_ticker, period_code)

if __name__ == "__main__":
    main()

