import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go

# Função para obter os dados da ação
def fetch_stock_data(tickers):
    data = {}
    for ticker in tickers:
        try:
            stock = yf.Ticker(ticker)
            info = stock.history(period="1d")
            if not info.empty:
                data[ticker] = {
                    "Nome": ticker,
                    "Preço": info["Close"].iloc[-1],
                    "Variação": info["Close"].pct_change().iloc[-1] * 100,
                    "Menor preço do dia": info["Low"].iloc[-1],
                    "Maior preço do dia": info["High"].iloc[-1],
                    "Preço de compra sugerido": info["Close"].iloc[-1] * 0.95,  # 5% de desconto
                    "Preço de venda sugerido": info["Close"].iloc[-1] * 1.05,  # 5% de acréscimo
                }
            else:
                data[ticker] = {"Nome": ticker, "Erro": "Sem dados disponíveis"}
        except Exception as e:
            data[ticker] = {"Nome": ticker, "Erro": f"Erro ao obter dados: {str(e)}"}

    return data

# Função para obter o gráfico de candle
def plot_candle_chart(ticker, period):
    stock = yf.Ticker(ticker)
    data = stock.history(period=period)
    fig = go.Figure(data=[go.Candlestick(x=data.index,
                                        open=data['Open'],
                                        high=data['High'],
                                        low=data['Low'],
                                        close=data['Close'])])
    fig.update_layout(title=f'Gráfico de {ticker} - Período: {period}',
                      xaxis_title='Data',
                      yaxis_title='Preço (R$)')
    return fig

# Lista de ações com a adição de 10 novos ativos
tickers = [
    "TSLA", "AMZN", "AAPL", "META", "NFLX", "NVDA", "GME", "AMC", "SPOT", "PLTR",
    "ROKU", "SQ", "ZM", "DOCU", "BYND", "COIN", "HOOD", "MRNA", "SNOW", "BA", "GS",
    "MSFT", "IBM", "BABA", "GOOG", "DIS", "WMT"
]

# Atualizar os dados das ações a cada 3 minutos
@st.cache(ttl=180)
def get_stock_data():
    return fetch_stock_data(tickers)

# Função para exibir as informações das ações
def display_stock_data():
    df = pd.DataFrame(get_stock_data()).T
    df = df.sort_values(by='Preço', ascending=False)  # Ordenando por preço (pode ser alterado conforme necessidade)

    st.write(df)

    return df

# Função principal de exibição
def main():
    st.title("Painel de Ações")

    # Exibir painel de ações
    st.subheader("Painel de Ações")
    df = display_stock_data()

    # Classificar por coluna ao clicar no título da coluna
    sort_by = st.selectbox("Classificar por", ['Preço', 'Variação', 'Menor preço do dia', 'Maior preço do dia'])
    if sort_by:
        df = df.sort_values(by=sort_by, ascending=False)

    # Adicionar gráfico de velas ao clicar no ativo
    selected_ticker = st.selectbox("Selecione uma Ação para ver o gráfico de velas", df['Nome'].tolist())

    # Filtro de período
    period = st.selectbox(
        "Selecione o período para o gráfico",
        ["1h", "3h", "6h", "12h", "24h", "5d", "15d", "1mo", "1y", "5y"]
    )

    if selected_ticker:
        fig = plot_candle_chart(selected_ticker, period)
        st.plotly_chart(fig)

# Executar a aplicação
if __name__ == "__main__":
    main()

