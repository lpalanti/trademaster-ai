import os
# Workaround para compatibilidade com protobuf
os.environ["PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION"] = "python"

import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
import requests
from datetime import datetime, timedelta
import pytz
from math import sqrt

# Configuração do Streamlit
st.set_page_config(layout="wide")

# Configurações do Telegram (substitua pelos seus dados)
BOT_TOKEN = '7971840892:AAH8sIg3iQUI7jQkMSd3YrYPaU4giRDVRQc'
CHAT_ID = '1963421158'

# Lista base de 20 ativos
TICKERS = [
    'TSLA','AMZN','AAPL','META','NFLX','NVDA','GME','AMC','SPOT','PLTR',
    'ROKU','SQ','ZM','DOCU','BYND','COIN','HOOD','MRNA','SNOW','MSFT'
]

# Fuso horário de São Paulo
TZ = pytz.timezone('America/Sao_Paulo')

# Envia alerta no Telegram

def send_telegram_alert(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {'chat_id': CHAT_ID, 'text': message}
    try:
        requests.post(url, data=payload)
    except Exception as e:
        st.warning(f"Erro ao enviar alerta: {e}")

# Calcula volatilidade histórica anualizada (3 meses)
@st.cache_data(ttl=3600)
def get_historical_volatility(tickers):
    vol_list = []
    for ticker in tickers:
        try:
            df = yf.download(ticker, period='3mo', interval='1d', progress=False)
            returns = df['Close'].pct_change().dropna()
            vol = float(returns.std() * sqrt(252) * 100)
            vol_list.append({'Ticker': ticker, 'Volatilidade Anual (%)': round(vol, 2)})
        except:
            continue
    vol_df = pd.DataFrame(vol_list).sort_values('Volatilidade Anual (%)', ascending=False).head(20).set_index('Ticker')
    return vol_df

# Busca dados intradiários e envia alertas de menor preço do dia
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
            close = float(df['Close'].iloc[-1])
            low = float(df['Low'].min())
            high = float(df['High'].max())
            open_ = float(df['Open'].iloc[0])
            variation = ((close - open_) / open_) * 100
            buy = close * 0.98
            sell = close * 1.02
            if close <= low:
                send_telegram_alert(f"🚨 {ticker} atinge menor preço do dia: R$ {close:.2f}")
            data[ticker] = {
                'Ticker': ticker,
                'Preço': round(close, 2),
                'Menor Preço do Dia': round(low, 2),
                'Maior Preço do Dia': round(high, 2),
                'Variação (%)': f"{variation:.2f}%",
                'Compra Sugerida': round(buy, 2),
                'Venda Sugerida': round(sell, 2),
                'Histórico': df
            }
        except Exception as e:
            st.warning(f"Erro ao baixar {ticker}: {e}")
    return data

# Exibe tabela de volatilidade

def display_volatility_table(vol_df):
    st.subheader("Top 20 por Volatilidade Histórica (3 meses)")
    st.dataframe(vol_df, use_container_width=True)

# Exibe tabela intradiária

def display_intraday_table(data):
    rows = []
    for info in data.values():
        rows.append({
            'Ticker': info['Ticker'],
            'Preço': info['Preço'],
            'Menor Preço do Dia': info['Menor Preço do Dia'],
            'Maior Preço do Dia': info['Maior Preço do Dia'],
            'Variação (%)': info['Variação (%)'],
            'Compra Sugerida': info['Compra Sugerida'],
            'Venda Sugerida': info['Venda Sugerida']
        })
    df = pd.DataFrame(rows).set_index('Ticker')
    st.subheader("📈 Dados Intradiários e Alertas")
    st.dataframe(df, use_container_width=True)
    return df

# Exibe gráfico de candlestick

def display_chart(hist, ticker):
    st.subheader(f"Candlestick de {ticker}")
    fig = go.Figure(data=[go.Candlestick(
        x=hist.index,
        open=hist['Open'], high=hist['High'], low=hist['Low'], close=hist['Close']
    )])
    fig.update_layout(xaxis_rangeslider_visible=False)
    st.plotly_chart(fig, use_container_width=True)

# Função principal

def main():
    st.title("📊 TradeMaster AI - Ações")
    # Volatilidade
    vol_df = get_historical_volatility(TICKERS)
    display_volatility_table(vol_df)
    # Intradiário
    stock_data = fetch_stock_data(TICKERS)
    if not stock_data:
        st.error("Nenhum dado disponível.")
        return
    intraday_df = display_intraday_table(stock_data)
    st.markdown("---")
    ticker = st.selectbox("Selecione ativo para gráfico", intraday_df.index.tolist())
    display_chart(stock_data[ticker]['Histórico'], ticker)

if __name__ == '__main__':
    main()

