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

# Verificar se os dados foram baixados corretamente
if data.empty:
    st.error('Não foi possível obter dados para o ticker fornecido.')
else:
    # Exibindo os dados históricos
    st.write('Dados Históricos:', data.tail())

    # Verificando se temos dados suficientes para calcular as médias móveis
    if len(data) >= 200:
        data['SMA50'] = data['Close'].rolling(window=50).mean()
        data['SMA200'] = data['Close'].rolling(window=200).mean()

        # Verificando se os valores de SMA50 e SMA200 não são NaN
        if not pd.isna(data['SMA50'].iloc[-1]) and not pd.isna(data['SMA200'].iloc[-1]):
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

            # Analisando os sinais
            if data['SMA50'].iloc[-1] > data['SMA200'].iloc[-1]:
                st.success('Sinal de Compra: SMA50 cruzou acima da SMA200')
            elif data['SMA50'].iloc[-1] < data['SMA200'].iloc[-1]:
                st.error('Sinal de Venda: SMA50 cruzou abaixo da SMA200')

        else:
            st.warning('Médias móveis não podem ser calculadas com dados insuficientes.')
    else:
        st.warning('Dados insuficientes para calcular as médias móveis. São necessários pelo menos 200 dados históricos.')

# Executar a aplicação
if __name__ == '__main__':
    st.write('Aplicação de Análise de Day Trade está rodando!')
