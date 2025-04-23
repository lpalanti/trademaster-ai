import streamlit as st
import pandas as pd
import yfinance as yf
import time
import requests
from datetime import datetime, timedelta
import plotly.graph_objects as go

st.set_page_config(layout="wide")

# Telegram config (substitua pelos seus dados)
BOT_TOKEN = "SEU_BOT_TOKEN"
CHAT_ID = "SEU_CHAT_ID"

@st.cache_data(ttl=180)
def fetch_stock_data(tickers):
    data = {}
    for ticker in tickers:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="1d", interval="1m")
        if hist.empty:
            continue
        price = hist["Close"].iloc[-1]
        low = hist["Low"].min()
        high = hist["High"].max()
        variation = ((price - hist["Open"].iloc[0]) / hist["Open"].iloc[0]) * 100

        # Alerta Telegram
        if price <= low:
            msg = f"🔔 {ticker} atingiu o menor preço do dia: R${price:.2f}"
            send_telegram_message(msg)

        data[ticker] = {
            "Ticker": ticker,
            "Menor Preço do Dia": f"R${low:.2f}",
            "Maior Preço do Dia": f"R${high:.2f}",
            "Preço": f"R${price:.2f}",
            "Variação": f"{variation:.2f}%",
            "Compra Sugerida": f"R${(price * 0.98):.2f}",
            "Venda Sugerida": f"R${(price * 1.02):.2f}",
            "Histórico": hist
        }
    return data

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message}
    try:
        requests.post(url, json=payload)
    except Exception as e:
        st.error(f"Erro ao enviar alerta para o Telegram: {e}")

def display_table(df):
    st.dataframe(df.sort_values("Ticker"), use_container_width=True)

def display_chart(hist, ticker):
    st.subheader(f"Gráfico de Candlestick - {ticker}")
    fig = go.Figure(data=[go.Candlestick(
        x=hist.index,
        open=hist["Open"],
        high=hist["High"],
        low=hist["Low"],
        close=hist["Close"]
    )])
    fig.update_layout(height=500, xaxis_rangeslider_visible=False)
    st.plotly_chart(fig, use_container_width=True)

def main():
    st.title("📈 Painel de Ações - TradeMaster AI")

    tickers = [
        "PETR4.SA", "VALE3.SA", "ITUB4.SA", "BBDC4.SA", "ABEV3.SA", "BBAS3.SA",
        "WEGE3.SA", "MGLU3.SA", "B3SA3.SA", "RENT3.SA", "LREN3.SA", "GGBR4.SA",
        "CSNA3.SA", "PRIO3.SA", "HAPV3.SA", "JBSS3.SA", "ELET3.SA", "COGN3.SA",
        "RADL3.SA", "ASAI3.SA"
    ]

    stock_data = fetch_stock_data(tickers)

    df = pd.DataFrame([
        {
            "Ticker": info["Ticker"],
            "Menor Preço do Dia": info["Menor Preço do Dia"],
            "Maior Preço do Dia": info["Maior Preço do Dia"],
            "Preço": info["Preço"],
            "Variação": info["Variação"],
            "Compra Sugerida": info["Compra Sugerida"],
            "Venda Sugerida": info["Venda Sugerida"],
        }
        for info in stock_data.values()
    ])

    selected_ticker = st.selectbox("🔍 Selecione um ativo para visualizar o gráfico", df["Ticker"])
    if selected_ticker:
        display_chart(stock_data[selected_ticker]["Histórico"], selected_ticker)

    st.markdown("## 📋 Tabela de Ações (clique no cabeçalho para ordenar)")
    display_table(df)

if __name__ == "__main__":
    main()

