import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import requests
from datetime import datetime, timedelta
import pytz

# Configuração do Streamlit
st.set_page_config(layout="wide")

# Configurações do Telegram (substitua pelos seus dados)
BOT_TOKEN = '7971840892:AAH8sIg3iQUI7jQkMSd3YrYPaU4giRDVRQc'
CHAT_ID = '1963421158'

# Lista de ativos
TICKERS = ['WEGE3.SA', 'PETR4.SA', 'VALE3.SA', 'ITUB4.SA', 'BBDC4.SA']

# Fuso horário
TZ = pytz.timezone('America/Sao_Paulo')

# Função para enviar alerta via Telegram

def send_telegram_alert(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {'chat_id': CHAT_ID, 'text': message}
    try:
        requests.post(url, data=payload)
    except Exception as e:
        st.warning(f"Erro ao enviar alerta para o Telegram: {e}")

# Função para obter dados de ações do dia
@st.cache_data(ttl=180)
def fetch_stock_data(tickers):
    data = {}
    now = datetime.now(TZ)
    start = (now - timedelta(days=1)).strftime('%Y-%m-%d')
    end = now.strftime('%Y-%m-%d')
    for ticker in tickers:
        try:
            df = yf.download(ticker, start=start, end=end, interval='1m', progress=False)
            if df.empty:
                continue
            price = float(df['Close'].iloc[-1])
            low = float(df['Low'].min())
            high = float(df['High'].max())
            open_price = float(df['Open'].iloc[0])
            variation = ((price - open_price) / open_price) * 100
            buy_price = price * 0.98
            sell_price = price * 1.02

            # Alerta Telegram se atingir menor preço do dia
            if price == low:
                send_telegram_alert(f"🚨 {ticker} atingiu o menor preço do dia: R$ {price:.2f}")

            data[ticker] = {
                'Ticker': ticker,
                'Menor Preço do Dia': round(low, 2),
                'Maior Preço do Dia': round(high, 2),
                'Preço': round(price, 2),
                'Variação (%)': f"{variation:.2f}%",
                'Compra Sugerida': round(buy_price, 2),
                'Venda Sugerida': round(sell_price, 2),
                'Histórico': df
            }
        except Exception as e:
            st.warning(f"Erro ao baixar dados de {ticker}: {e}")
    return data

# Função para exibir tabela

def display_table(df):
    st.dataframe(df, use_container_width=True)

# Função para exibir gráfico de candlestick

def display_chart(df, ticker):
    if df.empty:
        st.warning("Sem dados históricos para exibir.")
        return
    fig = go.Figure(data=[go.Candlestick(
        x=df.index,
        open=df['Open'],
        high=df['High'],
        low=df['Low'],
        close=df['Close']
    )])
    fig.update_layout(
        title=f"Candlestick de {ticker}",
        xaxis_title="Data",
        yaxis_title="Preço (R$)",
        xaxis_rangeslider_visible=False
    )
    st.plotly_chart(fig, use_container_width=True)

# Função principal

def main():
    st.title("📈 Painel de Ações - TradeMaster AI")
    data = fetch_stock_data(TICKERS)
    if not data:
        st.error("Nenhum dado disponível.")
        return
    df = pd.DataFrame([{k: v for k, v in {
        'Ticker': info['Ticker'],
        'Menor Preço do Dia': info['Menor Preço do Dia'],
        'Maior Preço do Dia': info['Maior Preço do Dia'],
        'Preço': info['Preço'],
        'Variação (%)': info['Variação (%)'],
        'Compra Sugerida': info['Compra Sugerida'],
        'Venda Sugerida': info['Venda Sugerida']
    }.items()} for info in data.values()]).set_index('Ticker')

    # Ordenação interativa
    sort_by = st.selectbox("Ordenar por", df.columns.tolist(), index=2)
    df = df.sort_values(by=sort_by, ascending=False)
    display_table(df)

    # Seleção para gráfico
    st.markdown("---")
    ticker = st.selectbox("Selecione ativo para gráfico", df.index.tolist())
    display_chart(data[ticker]['Histórico'], ticker)

if __name__ == '__main__':
    main()

