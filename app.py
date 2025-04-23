import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
import requests

# --- Funções auxiliares ---

def fetch_stock_data(tickers):
    """Busca dados de fechamento, mínimo, máximo e calcula variação e preços sugeridos."""
    data = {}
    for ticker in tickers:
        try:
            stock = yf.Ticker(ticker)
            info = stock.history(period="1d", interval="1m")
            if not info.empty:
                open_price = info["Open"].iloc[0]
                close_price = info["Close"].iloc[-1]
                low_price = info["Low"].min()
                high_price = info["High"].max()
                change_pct = ((close_price - open_price) / open_price) * 100
                buy_price = close_price * 0.95
                sell_price = close_price * 1.05

                data[ticker] = {
                    "Nome": ticker,
                    "Preço": close_price,
                    "Menor preço do dia": low_price,
                    "Maior preço do dia": high_price,
                    "Variação (%)": change_pct,
                    "Preço de compra sugerido": buy_price,
                    "Preço de venda sugerido": sell_price
                }
            else:
                data[ticker] = {
                    "Nome": ticker,
                    "Erro": "Sem dados disponíveis"
                }
        except Exception as e:
            data[ticker] = {
                "Nome": ticker,
                "Erro": f"Falha ao obter: {e}"
            }
    return data

@st.cache_data(ttl=180)
def get_stock_data(tickers):
    """Cache de 3 minutos para não refazer as requisições a cada atualização."""
    return fetch_stock_data(tickers)

def plot_candle_chart(ticker, period):
    """Desenha gráfico de velas para o ticker e período escolhido."""
    df = yf.Ticker(ticker).history(period=period)
    if df.empty:
        return None
    fig = go.Figure(data=[go.Candlestick(
        x=df.index,
        open=df["Open"],
        high=df["High"],
        low=df["Low"],
        close=df["Close"]
    )])
    fig.update_layout(
        title=f"Candle de {ticker} ({period})",
        xaxis_title="Data",
        yaxis_title="Preço (R$)"
    )
    return fig

# --- Lista de Ações (20 + 10 adicionais) ---
tickers = [
    "TSLA","AMZN","AAPL","META","NFLX","NVDA","GME","AMC","SPOT","PLTR",
    "ROKU","SQ","ZM","DOCU","BYND","COIN","HOOD","MRNA","SNOW",
    "MSFT","GOOG","DIS","WMT","BA","JPM","V","JNJ","PG","XOM"
]

# --- Funções de UI ---
def display_stock_table(df):
    """Exibe o DataFrame em tabela clicável e retorna o df para uso posterior."""
    st.dataframe(df, use_container_width=True)
    return df

def main():
    st.title("📈 Painel de Ações")
    st.markdown("Atualização a cada 3 minutos")

    # 1) Busca e exibe dados
    raw = get_stock_data(tickers)
    df = pd.DataFrame(raw).T

    # 2) Permite ordenar clicando no cabeçalho
    st.subheader("Tabela de Ações")
    df = display_stock_table(df)

    # 3) Seleção de ativo para o candle
    st.subheader("Gráfico de Velas")
    ticker = st.selectbox("Escolha o ticker:", df["Nome"].tolist())

    # 4) Filtro de período
    period = st.selectbox(
        "Período do Candle:",
        ["1h","3h","6h","12h","24h","5d","15d","1mo","1y","5y"]
    )

    if ticker:
        fig = plot_candle_chart(ticker, period)
        if fig:
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Não há dados para o período selecionado.")

if __name__ == "__main__":
    main()
