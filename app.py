import streamlit as st
import yfinance as yf
import pandas as pd
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
    ax.set_xlabel('Data')
    ax.set_ylabel('Preço')
    ax.legend()
    st.pyplot(fig)

# Função para exibir a interface de Streamlit
def display_interface():
    st.title("Automatização de Day Trade")
    st.sidebar.header("Parâmetros de Configuração")

    # Selecione o símbolo da ação
    symbol = st.sidebar.text_input("Símbolo da Ação", "PETR4.SA")

    # Coletar os dados de mercado
    data = get_data(symbol)
    if data is not None:
        # Verificar se a coluna 'Close' existe
        if 'Close' in data.columns and not data['Close'].isnull().all():
            sma = calculate_sma(data)

            # Exibir gráficos
            plot_data(data, sma)

            # Exibir os valores calculados
            if len(data) > 0:  # Verificar se há dados para calcular
                st.subheader(f"Último Preço de Fechamento de {symbol}: {data['Close'].iloc[-1]:.2f}")
                stop_loss = calculate_stop_loss(data)
                st.subheader(f"Stop Loss Calculado: {stop_loss:.2f}")
            else:
                st.warning("Não há dados suficientes para calcular o preço de fechamento ou stop loss.")
        else:
            st.error(f"A coluna 'Close' não foi encontrada nos dados para o símbolo {symbol}.")
    else:
        st.warning(f"Não foi possível recuperar os dados para o símbolo {symbol}.")

    # Permitir que o usuário decida a operação
    action = st.sidebar.radio("Ação", ("Comprar", "Vender", "Esperar"))
    if action == "Comprar":
        st.write("Ordem de compra registrada!")
    elif action == "Vender":
        st.write("Ordem de venda registrada!")
    else:
        st.write("Aguardando oportunidades...")

# Função principal para rodar a aplicação
def main():
    display_interface()

if __name__ == "__main__":
    main()
