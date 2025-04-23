import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import datetime
import pytz
import requests

# Configurações do Telegram (substitua com suas informações reais)
TELEGRAM_TOKEN = "6991361961:AAF0u9nbRLTCtqN-2iX7bl9d_4Hp7WcFZLQ"
TELEGRAM_CHAT_ID = "5454067892"

st.set_page_config(layout="wide")

# Função para enviar alerta via Telegram
def send_telegram_alert(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    try:
        requests.post(url, data=payload)
    except Exception as e:
        st.warning(f"Erro ao enviar mensagem no Telegram: {e}")

# Função para buscar dados de ações
def fetch_stock_data(tickers):
    stock_data = {}
    for ticker in tickers:
        try:
            hist = yf.download(ticker, period="1d", interval="5m")
            if hist.empty:
                continue
            price = hist["Close"].iloc[-1]
            min_price = hist["Low"].min()
            max_price = hist["High"].max()
            open_price = hist["Open"].iloc[0]
            variation = ((price - open_price) / open_price) * 100
            buy_price = price * 0.98
            sell_price = price * 1.02

            # Alerta se o preço atual for igual ao menor do dia
            if price == min_price:
                send_telegram_alert(f"🚨 Alerta: {ticker} atingiu o menor preço do dia! Preço atual: R$ {price:.2f}")

            stock_data[ticker] = {
                "Ticker": ticker,
                "Preço": price,
                "Menor Preço do Dia": min_price,
                "Maior Preço do Dia": max_price,
                "Variação": f"{variation:.2f}%",
                "Compra Sugerida": buy_price,
                "Venda Sugerida": sell_price,
                "Histórico": hist,
            }
        except Exception as e:
            print(f"Erro ao baixar dados de {ticker}: {e}")
    return stock_data

# Função para exibir o gráfico
def display_chart(hist, ticker):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=hist.index, y=hist["Close"], mode="lines", name="Preço"))
    fig.update_layout(title=f"Histórico intradiário de {ticker}", xaxis_title="Horário", yaxis_title="Preço (R$)")
    st.plotly_chart(fig, use_container_width=True)

# Função para exibir tabela com destaques
def display_table(df):
    styled_df = df.style.applymap(lambda v: "color: green;" if isinstance(v, str) and "-" not in v and "%" in v else ("color: red;" if isinstance(v, str) and "-" in v else ""), subset=["Variação"])
    st.dataframe(styled_df, use_container_width=True, hide_index=True)

# Função principal
def main():
    st.title("📈 Painel de Ações - TradeMaster AI")

    tickers = [
        "PETR4.SA", "VALE3.SA", "ITUB4.SA", "BBDC4.SA", "ABEV3.SA", "BBAS3.SA",
        "WEGE3.SA", "MGLU3.SA", "B3SA3.SA", "RENT3.SA", "LREN3.SA", "GGBR4.SA",
        "CSNA3.SA", "PRIO3.SA", "HAPV3.SA", "JBSS3.SA", "ELET3.SA", "COGN3.SA",
        "RADL3.SA", "ASAI3.SA"
    ]

    stock_data = fetch_stock_data(tickers)

    if not stock_data:
        st.error("❌ Nenhum dado foi carregado. Verifique a conexão ou se o mercado está fechado.")
        return

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

    if df.empty or "Ticker" not in df.columns:
        st.error("❌ A tabela de dados está vazia ou malformada.")
        return

    selected_ticker = st.selectbox("🔍 Selecione um ativo para visualizar o gráfico", df["Ticker"].tolist())
    if selected_ticker:
        display_chart(stock_data[selected_ticker]["Histórico"], selected_ticker)

    st.markdown("## 📋 Tabela de Ações (clique no cabeçalho para ordenar)")
    display_table(df)

if __name__ == "__main__":
    main()

