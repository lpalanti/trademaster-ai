# app.py
import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objs as go

# ---------------------
# Funções auxiliares
# ---------------------
def calcular_indicadores(df):
    df['MM9'] = df['Close'].rolling(window=9).mean()
    df['MM21'] = df['Close'].rolling(window=21).mean()
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))
    return df

def grafico_ativo(df, ticker):
    fig = go.Figure()

    fig.add_trace(go.Candlestick(
        x=df.index,
        open=df['Open'],
        high=df['High'],
        low=df['Low'],
        close=df['Close'],
        name='Candles'
    ))

    fig.add_trace(go.Scatter(x=df.index, y=df['MM9'], line=dict(color='blue', width=1.5), name='MM9'))
    fig.add_trace(go.Scatter(x=df.index, y=df['MM21'], line=dict(color='orange', width=1.5), name='MM21'))

    fig.update_layout(title=f'Gráfico de {ticker} com MM9/MM21', xaxis_rangeslider_visible=False)
    return fig

def grafico_rsi(df):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df['RSI'], line=dict(color='purple', width=1.5), name='RSI'))
    fig.add_hline(y=70, line_dash="dash", line_color="red")
    fig.add_hline(y=30, line_dash="dash", line_color="green")
    fig.update_layout(title='RSI (14 períodos)', yaxis_range=[0, 100])
    return fig

# ---------------------
# Lista de ativos por setor
# ---------------------
ativos = {
    "🏦 Bancos": ["ITUB4.SA", "BBDC4.SA", "BBAS3.SA", "SANB11.SA"],
    "🛒 Varejo & Consumo": ["MGLU3.SA", "VIIA3.SA", "LREN3.SA", "ABEV3.SA"],
    "⚙️ Indústrias & Serviços": ["WEGE3.SA", "EMBR3.SA", "RADL3.SA", "SUZB3.SA"],
    "📉 Small Caps": ["CVCB3.SA", "OIBR3.SA", "IRBR3.SA", "AZUL4.SA"],
    "💡 Outros Setores": ["TOTS3.SA", "ELET3.SA", "EQTL3.SA", "HAPV3.SA"],
}

todos_tickers = sum(ativos.values(), [])

# ---------------------
# Streamlit App
# ---------------------
st.title("📈 TradeMaster AI – Análise Técnica com Gráficos")

ativo_escolhido = st.selectbox("🔍 Selecione um ativo para análise técnica:", todos_tickers)

dados = yf.download(ativo_escolhido, period="3mo", interval="1d", progress=False)
dados = calcular_indicadores(dados)

# Exibir gráficos
st.plotly_chart(grafico_ativo(dados, ativo_escolhido.replace(".SA", "")), use_container_width=True)
st.plotly_chart(grafico_rsi(dados), use_container_width=True)

