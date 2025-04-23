import streamlit as st
import pandas as pd
import yfinance as yf
import time
import plotly.graph_objs as go

st.set_page_config(layout="wide")

st.title("Painel de Ações")

# Tickers a serem monitorados
tickers = {
    "PETR4.SA": "Petrobras",
    "VALE3.SA": "Vale",
    "ITUB4.SA": "Itaú Unibanco",
    "BBDC4.SA": "Bradesco",
    "BBAS3.SA": "Banco do Brasil",
    "ABEV3.SA": "Ambev",
    "WEGE3.SA": "Weg",
    "MGLU3.SA": "Magazine Luiza",
    "RENT3.SA": "Localiza",
    "LREN3.SA": "Lojas Renner",
    "JBSS3.SA": "JBS",
    "B3SA3.SA": "B3",
    "CSNA3.SA": "CSN",
    "GGBR4.SA": "Gerdau",
    "EGIE3.SA": "Engie Brasil"
}

# Função para buscar dados
@st.cache_data(ttl=180)
def fetch_stock_data(tickers):
    data = {}
    for ticker in tickers:
        try:
            info = yf.download(ticker, period="1d", interval="1m")
            if info.empty:
                continue
            preco_atual = info["Close"].iloc[-1]
            preco_abertura = info["Open"].iloc[0]
            variacao = ((preco_atual - preco_abertura) / preco_abertura) * 100
            menor_preco = info["Low"].min()
            maior_preco = info["High"].max()
            preco_compra = preco_atual * 0.95
            preco_venda = preco_atual * 1.05
            data[ticker] = {
                "Ativo": tickers[ticker],
                "Sigla": ticker,
                "Preço": round(preco_atual, 2),
                "Variação (%)": round(variacao, 2),
                "Menor Preço": round(menor_preco, 2),
                "Maior Preço": round(maior_preco, 2),
                "Preço Compra (sug.)": round(preco_compra, 2),
                "Preço Venda (sug.)": round(preco_venda, 2),
            }
        except:
            continue
    return data

# Exibir os dados
def display_stock_data():
    df = pd.DataFrame(fetch_stock_data(tickers)).T
    df = df.sort_values(by="Ativo")
    st.dataframe(df, use_container_width=True)
    return df

# Gráfico
def show_candle_chart(ticker, periodo):
    try:
        data = yf.download(ticker, period=periodo, interval="15m")
        if data.empty:
            st.warning("Sem dados para o período selecionado.")
            return

        fig = go.Figure(data=[go.Candlestick(x=data.index,
                        open=data['Open'],
                        high=data['High'],
                        low=data['Low'],
                        close=data['Close'])])

        fig.update_layout(title=f"Gráfico de Candlestick: {ticker}", xaxis_title="Data", yaxis_title="Preço")
        st.plotly_chart(fig, use_container_width=True)
    except:
        st.error("Erro ao carregar gráfico.")

# Interface
df = display_stock_data()

st.markdown("## Gráfico do Ativo")

ticker_selecionado = st.selectbox("Selecione o ativo para ver o gráfico:", df["Sigla"])
periodo = st.selectbox("Selecione o período:", ["1h", "3h", "6h", "12h", "1d", "5d", "15d", "1mo", "1y", "5y"])

if ticker_selecionado:
    show_candle_chart(ticker_selecionado, periodo)
