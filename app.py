import streamlit as st
import pandas as pd
import yfinance as yf
import datetime
import matplotlib.pyplot as plt
import mplfinance as mpf

st.set_page_config(page_title="TradeMasterAI", layout="wide")

st.markdown("""
    <style>
    body {
        background-color: black;
        color: white;
    }
    .stApp {
        background-color: black;
        color: white;
    }
    .css-18e3th9 {
        background-color: black;
        color: white;
    }
    .stDataFrame, .stMetric {
        background-color: #111;
        color: white;
    }
    .css-1d391kg input {
        background-color: #333;
        color: white;
    }
    </style>
""", unsafe_allow_html=True)

st.title("📈 TradeMasterAI - Painel de Simulação Day Trade")
st.markdown("Dados reais dos ativos | Atualiza a cada 3 minutos")

# Lista de ativos disponíveis
ativos = {
    "Bitcoin (BTC-USD)": "BTC-USD",
    "Mini Índice (WIN=F)": "WIN=F",
    "Petrobras (PETR4.SA)": "PETR4.SA",
    "Vale (VALE3.SA)": "VALE3.SA",
    "Apple (AAPL)": "AAPL",
    "Tesla (TSLA)": "TSLA"
}

ativo_nome = st.selectbox("Selecione o ativo para visualizar:", list(ativos.keys()))
ativo_codigo = ativos[ativo_nome]

# Intervalo dos dados (últimas 3 horas)
fim = datetime.datetime.now()
inicio = fim - datetime.timedelta(hours=3)

# Função para calcular médias móveis e sugerir operações
@st.cache_data(show_spinner=False)
def sugerir_operacoes_com_sma(ativo_dict):
    sugestoes = []
    graficos = {}
    ranking = []
    for nome, codigo in ativo_dict.items():
        dados = yf.download(tickers=codigo, start=inicio, end=fim, interval="3m")
        if not dados.empty:
            # Calcular SMA de 5 e 10 períodos
            dados['SMA_5'] = dados['Close'].rolling(window=5).mean()
            dados['SMA_10'] = dados['Close'].rolling(window=10).mean()

            # Verificar cruzamento das SMAs (sinal de compra/venda)
            cruzamento = ""
            if dados['SMA_5'].iloc[-1] > dados['SMA_10'].iloc[-1]:
                cruzamento = "Sinal de Compra"
            elif dados['SMA_5'].iloc[-1] < dados['SMA_10'].iloc[-1]:
                cruzamento = "Sinal de Venda"

            preco_minimo = dados['Close'].min()
            preco_maximo = dados['Close'].max()
            preco_atual = dados['Close'].iloc[-1]

            # Calcular potencial de lucro
            potencial_lucro = (preco_maximo - preco_atual) / preco_atual * 100

            sugestoes.append({
                "Ativo": nome,
                "Preço Ideal para Compra": f"R$ {preco_minimo:.2f}",
                "Preço Ideal para Venda": f"R$ {preco_maximo:.2f}",
                "Preço Atual": f"R$ {preco_atual:.2f}",
                "Potencial de Lucro (%)": f"{potencial_lucro:.2f}%",
                "Sinal": cruzamento
            })

            # Adicionar gráfico de candles
            dados_candles = dados[['Open', 'High', 'Low', 'Close']]
            fig, axes = plt.subplots(1, 1, figsize=(10, 6))
            mpf.plot(dados_candles, type='candle', ax=axes, title=nome)
            graficos[nome] = fig

            # Calcular o desvio atual do preço em relação à média
            media = dados['Close'].mean()
            desvio_percentual = ((preco_atual - media) / media) * 100
            ranking.append((nome, desvio_percentual))

    # Ordenar o ranking de ativos por desvio percentual
    ranking.sort(key=lambda x: x[1], reverse=True)
    return pd.DataFrame(sugestoes), graficos, ranking

# Exibir sugestões de compra e venda com SMA
st.subheader("💡 Sugestões de Operações com Base nas Últimas 3 Horas (Com SMA)")
df_operacoes, graficos_operacoes, ranking_ativos = sugerir_operacoes_com_sma(ativos)
st.dataframe(df_operacoes, use_container_width=True)

# Exibir gráficos de candles dos ativos
for nome, fig in graficos_operacoes.items():
    with st.expander(f"Visualização: {nome}"):
        st.pyplot(fig)

# Ranking de ativos por desvio atual vs média
st.subheader("🏅 Ranking de Ativos por Desvio Atual vs Média")
ranking_df = pd.DataFrame(ranking_ativos, columns=["Ativo", "Desvio Percentual (%)"])
st.dataframe(ranking_df, use_container_width=True)

st.markdown("""
<div style='text-align:center'>
    <small>Atualizado em: {}</small>
</div>
""".format(datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")), unsafe_allow_html=True)


