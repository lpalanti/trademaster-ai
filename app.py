import streamlit as st
import yfinance as yf
import pandas as pd
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

# Lista dos 20 ativos originalmente mencionados
TICKERS = [
    'TSLA','AMZN','AAPL','META','NFLX','NVDA','GME','AMC','SPOT','PLTR',
    'ROKU','SQ','ZM','DOCU','BYND','COIN','HOOD','MRNA','SNOW','SPOT'
]

# Fuso horário de São Paulo
TZ = pytz.timezone('America/Sao_Paulo')

# Função para enviar alerta via Telegram
def send_telegram_alert(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {'chat_id': CHAT_ID, 'text': message}
    try:
        requests.post(url, data=payload)
    except Exception as e:
        st.warning(f"Erro ao enviar alerta para o Telegram: {e}")

# Cálculo de volatilidade histórica (anualizada sobre 3 meses)
@st.cache_data(ttl=3600)
def get_historical_volatility(tickers):
    vol_list = []
    for ticker in tickers:
        try:
            df = yf.download(ticker, period='3mo', interval='1d', progress=False)
            returns = df['Close'].pct_change().dropna()
            vol = float(returns.std() * sqrt(252) * 100)  # anualizada em %
            vol_list.append({'Ticker': ticker, 'Volatilidade Anual (%)': round(vol,2)})
        except Exception:
            continue
    vol_df = pd.DataFrame(vol_list)
    vol_df = vol_df.sort_values(by='Volatilidade Anual (%)', ascending=False).head(20)
    return vol_df

# Obter dados intradiários e alertas
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
            # Alerta se atingir menor preço
            if price == low:
                send_telegram_alert(f"🚨 {ticker} atingiu o menor preço do dia: R$ {price:.2f}")
            data[ticker] = {
                'Ticker': ticker,
                'Preço': round(price,2),
                'Menor Preço do Dia': round(low,2),
                'Maior Preço do Dia': round(high,2),
                'Variação (%)': f"{variation:.2f}%",
                'Compra Sugerida': round(buy_price,2),
                'Venda Sugerida': round(sell_price,2),
                'Histórico': df
            }
        except Exception as e:
            st.warning(f"Erro ao baixar dados de {ticker}: {e}")
    return data

# Exibir tabela de volatilidade histórica

def display_volatility_table(df):
    st.subheader("Top 20 Ativos por Volatilidade Histórica (3 meses)")
    st.dataframe(df, use_container_width=True)

# Exibir tabela intradiária

def display_intraday_table(df):
    st.subheader("📈 Dados Intradiários e Alertas")
    st.dataframe(df.drop(columns=['Histórico']), use_container_width=True)

# Exibir gráfico de candlestick

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
    fig.update_layout(title=f"Candlestick de {ticker}", xaxis_title="Hora", yaxis_title="Preço (R$)", xaxis_rangeslider_visible=False)
    st.plotly_chart(fig, use_container_width=True)

# Main
def main():
    st.title("📊 TradeMaster AI - Ações")
    # Volatilidade histórica
    vol_df = get_historical_volatility(TICKERS)
    display_volatility_table(vol_df)
    # Intradiário e alertas
    stock_data = fetch_stock_data(TICKERS)
    if not stock_data:
        st.error("Nenhum dado disponível.")
        return
    intraday_df = pd.DataFrame([{k: v for k,v in item.items() if k!='Histórico'} for item in stock_data.values()]).set_index('Ticker')
    display_intraday_table(intraday_df)
    # Seleção para gráfico
    st.markdown("---")
    ticker = st.selectbox("Selecione ativo para gráfico", intraday_df.index.tolist())
    display_chart(stock_data[ticker]['Histórico'], ticker)

if __name__ == '__main__':
    main()

