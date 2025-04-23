import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

# Função para obter os dados do estoque com cache
@st.cache
def get_stock_data(ticker):
    return yf.download(ticker, period="1y")  # Limitar o período para 1 ano

# Função para calcular médias móveis
@st.cache
def calculate_moving_averages(data):
    data['SMA50'] = data['Close'].rolling(window=50).mean()
    data['SMA200'] = data['Close'].rolling(window=200).mean()
    return data

# Interface do usuário
st.title("Análise de Day Trade com Indicadores Técnicos")

# Campo de entrada para o ticker
ticker = st.text_input("Digite o código da ação:", "AAPL")

# Carregar dados
data = get_stock_data(ticker)
data = calculate_moving_averages(data)

# Exibir os dados em formato de tabela
st.write("Dados históricos:", data.tail())

# Plotar o gráfico de preços com médias móveis
st.subheader("Gráfico de Preços com Médias Móveis")

fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(data.index, data['Close'], label='Preço de Fechamento', color='blue')
ax.plot(data.index, data['SMA50'], label='SMA 50', linestyle='--', color='orange')
ax.plot(data.index, data['SMA200'], label='SMA 200', linestyle='--', color='green')
ax.set_xlabel('Data')
ax.set_ylabel('Preço')
ax.set_title(f'Gráfico de {ticker}')
ax.legend()
st.pyplot(fig)

# Analisando cruzamento de médias móveis
if data['SMA50'].iloc[-1] > data['SMA200'].iloc[-1]:
    st.write(f'O {ticker} está em tendência de alta (SMA50 > SMA200)')
else:
    st.write(f'O {ticker} está em tendência de baixa (SMA50 < SMA200)')

