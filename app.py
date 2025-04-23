import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import telegram
from datetime import datetime, timedelta
import pytz

# Função para enviar alerta no Telegram
def send_telegram_alert(message):
    bot = telegram.Bot(token='7971840892:AAH8sIg3iQUI7jQkMSd3YrYPaU4giRDVRQc')
    chat_id = '1963421158'
    bot.sendMessage(chat_id=chat_id, text=message)

# Função para obter dados de ações
def get_stock_data(ticker, start_date, end_date):
    df = yf.download(ticker, start=start_date, end=end_date, interval='1m')
    return df

# Função para construir o gráfico
def plot_stock_chart(df, ticker):
    fig = go.Figure(data=[go.Candlestick(x=df.index,
                                        open=df['Open'],
                                        high=df['High'],
                                        low=df['Low'],
                                        close=df['Close'],
                                        name=ticker)])
    fig.update_layout(title=f'Gráfico de {ticker}',
                      xaxis_title='Data',
                      yaxis_title='Preço',
                      template='plotly_dark')
    return fig

# Função para verificar o menor valor do dia
def check_lowest_price_alert(df, ticker):
    min_price = df['Low'].min()
    min_price_time = df['Low'].idxmin()
    return min_price, min_price_time

# Função principal do app
def main():
    # Fuso horário de São Paulo
    tz = pytz.timezone('America/Sao_Paulo')
    now = datetime.now(tz)

    # Período de dados: de 1 dia atrás até o momento atual
    start_date = (now - timedelta(days=1)).strftime('%Y-%m-%d')
    end_date = now.strftime('%Y-%m-%d')

    # Lista de tickers
    tickers = ['WEGE3.SA', 'PETR4.SA', 'VALE3.SA', 'ITUB4.SA', 'BBDC4.SA']

    # Seleção do ativo
    selected_ticker = st.selectbox("🔍 Selecione um ativo para visualizar o gráfico", tickers)

    # Obter dados históricos
    df = get_stock_data(selected_ticker, start_date, end_date)

    # Plotar gráfico
    st.plotly_chart(plot_stock_chart(df, selected_ticker))

    # Verificar e exibir o menor preço do dia
    min_price, min_price_time = check_lowest_price_alert(df, selected_ticker)
    st.write(f'O menor preço de {selected_ticker} hoje foi {min_price} às {min_price_time.strftime("%H:%M:%S")}.')

    # Enviar alerta no Telegram
    send_telegram_alert(f'Alerta de preço baixo: {selected_ticker} atingiu o menor preço de {min_price} às {min_price_time.strftime("%H:%M:%S")}.')

if __name__ == "__main__":
    main()

