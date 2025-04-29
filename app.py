import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Função para coletar dados do Yahoo Finance
def get_data(symbol, period='1d', interval='5m'):
    try:
        data = yf.download(symbol, period=period, interval=interval)
        if data.empty:
            raise ValueError(f"Não foram encontrados dados para o símbolo {symbol}")
        return data
    except Exception as e:
        st.error(f"Erro ao coletar dados para {symbol}: {e}")
        return None

# Função para calcular média móvel simples
def calculate_sma(data, window=20):
    return data['Close'].rolling(window=window).mean()

# Função para calcular o Stop Loss baseado na volatilidade (ATR)
def calculate_stop_loss(data, risk_factor=1.5):
    atr = data['High'] - data['Low']
    stop_loss = data['Close'][-1] - (risk_factor * atr[-1])
    return stop_loss

# Função para exibir o gráfico
def plot_data(data, sma):
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(data.index, data['Close'], label='Preço de Fechamento', color='blue')
    ax.plot(data.index, sma, label='Média Móvel', color='orange')
    ax.set_title("Gráfico de Preços e Média Móvel")
    ax.set_xlabel_
