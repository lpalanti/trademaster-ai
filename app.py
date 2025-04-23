import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
import requests
from datetime import datetime, time
import pytz

# Configuração do Streamlit
st.set_page_config(layout="wide")

# Configurações do Telegram (substitua pelos seus dados)
BOT_TOKEN = "7971840892:AAH8sIg3iQUI7jQkMSd3YrYPaU4giRDVRQc"
CHAT_ID = "1963421158"

# Lista de ativos
TICKERS = [
    "PETR4.SA", "VALE3.SA", "ITUB4.SA", "BBDC4.SA", "ABEV3.SA",
    "WEGE3.SA", "BBAS3.SA", "MGLU3.SA", "LREN3.SA", "RENT3.SA",
    "PRIO3.SA", "CSNA3.SA", "GGBR4.SA", "BRFS3.SA", "RAIL3.SA",
    "JBSS3.SA", "EGIE3.SA", "CMIG4.SA", "CPLE6.SA", "CYRE3.SA"
]

# Fuso horário de São Paulo
TZ = pytz.timezone("America/Sao_Paulo")

# Função para enviar alerta via Telegram
def send_telegram_alert(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message}
    try:
        requests.post(url, data=payload)
    except Exception as e:
        st.warning(f"Erro ao enviar alerta para o Telegram: {e}")

# Busca dados do dia atual usando start/end em vez de period=1d
@st.cache_data(ttl=180)
def fetch_stock_data(tickers):
    data = {}
    now = datetime.now(TZ)
    start_of_day = TZ.localize(datetime.combine(now.date(), time(0, 0)))
    for ticker in tickers:
        try:
            # Converter para UTC strings
            start_str = start_of_day.astimezone(pytz.UTC).strftime("%Y-%m-%d %H:%M:%S")
            end_str = now.astimezone(pytz.UTC).strftime("%Y-%m-%d %H:%M:%S")
            hist = yf.download(
                ticker,
                start=start_str,
                end=end_str,
                interval="5m",
                progress=False
            )
            if hist.empty:
                continue
            price = float(hist["Close"].iloc[-1])
            min_price = float(hist["Low"].min())
            max_price = float(hist["High"].max())
            open_price = float(hist["Open"].iloc[0])
            variation = ((price - open_price) / open_price) * 100
            buy_price = price * 0.98
            sell_price = price * 1.02

            # Envia alerta se preço igual ao menor do dia
            if price == min_price:
                send_telegram_alert(
                    f"🚨 Alerta: {ticker} atingiu o menor preço do dia! R$ {price:.2f}"
                )

            data[ticker] = {
                "Ticker": ticker,
                "Preço": round(price, 2),
                "Menor Preço do Dia": round(min_price, 2),
                "Maior Preço do Dia": round(max_price, 2),
                "Variação (%)": f"{variation:.2f}%",
                "Compra Sugerida": round(buy_price, 2),
                "Venda Sugerida": round(sell_price, 2),
                "Histórico": hist
            }
        except Exception as e:
            st.warning(f"Erro ao baixar dados de {ticker}: {e}")
    return data

# Exibe tabela de dados

def display_table(df):
    st.dataframe(df, use_container_width=True)

# Exibe gráfico de candlestick
def display_chart(hist, ticker):
    if hist.empty:
        st.warning("Sem dados históricos para exibir.")
        return
    fig = go.Figure(data=[go.Candlestick(
        x=hist.index,
        open=hist['Open'],
        high=hist['High'],
        low=hist['Low'],
        close=hist['Close']
    )])
    fig.update_layout(
        title=f"Gráfico de Candlestick - {ticker}",
        xaxis_title="Data",
        yaxis_title="Preço (R$)",
        xaxis_rangeslider_visible=False
    )
    st.plotly_chart(fig, use_container_width=True)

# Função principal

def main():
    st.title("📈 Painel de Ações - TradeMaster AI")

    stock_data = fetch_stock_data(TICKERS)
    if not stock_data:
        st.error("❌ Nenhum dado carregado. Verifique conexão ou mercado fechado.")
        return

    # Monta DataFrame para exibir
    df = pd.DataFrame([{
        "Ticker": info["Ticker"],
        "Menor Preço do Dia": info["Menor Preço do Dia"],
        "Maior Preço do Dia": info["Maior Preço do Dia"],
        "Preço": info["Preço"],
        "Variação (%)": info["Variação (%)"],
        "Compra Sugerida": info["Compra Sugerida"],
        "Venda Sugerida": info["Venda Sugerida"]
    } for info in stock_data.values()])

    # Ordenação interativa
    sort_by = st.selectbox("Ordenar por:", df.columns.tolist(), index=2)
    df = df.sort_values(by=sort_by, ascending=False)

    display_table(df)

    # Gráfico
    st.markdown("---")
    ticker = st.selectbox("Selecione ativo para gráfico", df["Ticker"].tolist())
    display_chart(stock_data[ticker]["Histórico"], ticker)

if __name__ == "__main__":
    main()

