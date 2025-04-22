import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta  # Substituindo TA-Lib por pandas_ta
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from datetime import datetime

# Função para carregar dados financeiros de um ativo
def carregar_dados(ativo):
    data_inicial = datetime.now() - pd.Timedelta(days=30)  # Dados dos últimos 30 dias
    dados = yf.download(ativo, start=data_inicial.strftime('%Y-%m-%d'))
    return dados

# Função para calcular os indicadores técnicos
def calcular_indicadores(dados):
    # Média Móvel Simples (SMA) de 50 e 200 períodos
    dados['SMA50'] = dados['Close'].rolling(window=50).mean()
    dados['SMA200'] = dados['Close'].rolling(window=200).mean()
    
    # Índice de Força Relativa (RSI) de 14 períodos
    dados['RSI'] = ta.rsi(dados['Close'], length=14)  # Usando pandas_ta para o RSI
    
    return dados

# Função para gerar gráfico com os dados e indicadores
def gerar_grafico(dados, ativo):
    fig = go.Figure()

    # Adicionando gráfico de preços de fechamento
    fig.add_trace(go.Candlestick(x=dados.index,
                                 open=dados['Open'],
                                 high=dados['High'],
                                 low=dados['Low'],
                                 close=dados['Close'],
                                 name='Candlestick'))
    
    # Adicionando a SMA50 e SMA200
    fig.add_trace(go.Scatter(x=dados.index, y=dados['SMA50'], mode='lines', name='SMA50', line={'color': 'blue'}))
    fig.add_trace(go.Scatter(x=dados.index, y=dados['SMA200'], mode='lines', name='SMA200', line={'color': 'red'}))
    
    # Adicionando o gráfico de RSI
    fig.add_trace(go.Scatter(x=dados.index, y=dados['RSI'], mode='lines', name='RSI', line={'color': 'green'}))

    # Layout do gráfico
    fig.update_layout(
        title=f'Gráfico de {ativo} - Últimos 30 dias',
        xaxis_title='Data',
        yaxis_title='Preço',
        yaxis2=dict(title='RSI', overlaying='y', side='right'),
        xaxis_rangeslider_visible=False
    )

    return fig

# Função para sugerir momentos de compra e venda
def sugerir_compras_vendas(dados):
    # Sugestão de compra quando SMA50 cruza acima de SMA200
    compra = dados[dados['SMA50'] > dados['SMA200']].tail(1)
    
    # Sugestão de venda quando SMA50 cruza abaixo de SMA200
    venda = dados[dados['SMA50'] < dados['SMA200']].tail(1)
    
    return compra, venda

# Função para exibir os dados e sugestões no Streamlit
def exibir_dados():
    ativo = st.text_input('Digite o símbolo do ativo (ex: AAPL para Apple)', 'AAPL')

    # Carregando os dados
    dados = carregar_dados(ativo)
    dados = calcular_indicadores(dados)
    
    # Gerando gráfico
    st.plotly_chart(gerar_grafico(dados, ativo), use_container_width=True)
    
    # Mostrando sugestões
    compra, venda = sugerir_compras_vendas(dados)

    st.header('Sugestões de Operações')
    if not compra.empty:
        st.subheader('Momento de Compra:')
        st.write(compra)
    else:
        st.subheader('Sem sugestão de compra no momento')

    if not venda.empty:
        st.subheader('Momento de Venda:')
        st.write(venda)
    else:
        st.subheader('Sem sugestão de venda no momento')

# Função principal que organiza o fluxo do app
def main():
    st.title("Assistente de Day Trade")
    st.sidebar.header("Configurações")

    exibir_dados()

if __name__ == "__main__":
    main()
