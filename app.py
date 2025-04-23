import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objs as go

# Título da aplicação
st.title('Ferramenta de Análise para Day Trade')

# Coletando o ticker de uma ação através de input
ticker = st.text_input('Digite o Ticker da Ação:', 'AAPL')

# Baixando os dados históricos da ação
data = yf.download(ticker, start='2020-01-01', end='2025-01-01')

# Exibindo os dados históricos
st.write('Dados Históricos:', data.tail())

# Calculando indicadores técnicos
data['SMA50'] = data['Close'].rolling(window=50).mean()
data['SMA200'] = data['Close'].rolling(window=200).mean()

# Plotando os gráficos com Plotly
fig = go.Figure()

fig.add_trace(go.Candlestick(
    x=data.index,
    open=data['Open'],
    high=data['High'],
    low=data['Low'],
    close=data['Close'],
    name='Preço'
))

fig.add_trace(go.Scatter(x=data.index, y=data['SMA50'], mode='lines', name='SMA 50', line=dict(color='orange')))
fig.add_trace(go.Scatter(x=data.index, y=data['SMA200'], mode='lines', name='SMA 200', line=dict(color='red')))

# Exibindo o gráfico
st.plotly_chart(fig)

# Adicionando alertas
if data['SMA50'].iloc[-1] > data['SMA200'].iloc[-1]:
    st.success('Sinal de Compra: SMA50 cruzou acima da SMA200')
elif data['SMA50'].iloc[-1] < data['SMA200'].iloc[-1]:
    st.error('Sinal de Venda: SMA50 cruzou abaixo da SMA200')

# Executar a aplicação
if __name__ == '__main__':
    st.write('Aplicação de Análise de Day Trade está rodando!')

