import streamlit as st
import pandas as pd
import yfinance as yf
import datetime
import matplotlib.pyplot as plt

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
    "Petrobras (PETR4.SA)": "PETR4.SA"
}

ativo_nome = st.selectbox("Selecione o ativo para visualizar:", list(ativos.keys()))
ativo_codigo = ativos[ativo_nome]

# Intervalo dos dados (últimas 3 horas)
fim = datetime.datetime.now()
inicio = fim - datetime.timedelta(hours=3)

# Função para calcular sugestão de compra e venda
@st.cache_data(show_spinner=False)
def sugestao_operacoes(ativo_dict):
    sugestoes = []
    graficos = {}
    for nome, codigo in ativo_dict.items():
        dados = yf.download(tickers=codigo, start=inicio, end=fim, interval="3m")
        if not dados.empty:
            preco_minimo = dados['Close'].min()
            preco_maximo = dados['Close'].max()
            preco_atual = dados['Close'].iloc[-1]
            sugestoes.append({
                "Ativo": nome,
                "Preço Ideal para Compra": f"R$ {preco_minimo:.2f}",
                "Preço Ideal para Venda": f"R$ {preco_maximo:.2f}",
                "Preço Atual": f"R$ {preco_atual:.2f}"
            })

            # Preparar gráfico
            fig, ax = plt.subplots()
            barras = ax.bar(["Compra", "Venda", "Atual"], [preco_minimo, preco_maximo, preco_atual], color=["green", "red", "gray"])
            ax.set_title(f"{nome}")
            ax.set_ylabel("Preço (R$)")
            ax.bar_label(barras, fmt='%.2f')
            graficos[nome] = fig

    return pd.DataFrame(sugestoes), graficos

# Exibir sugestões visuais de compra e venda
st.subheader("💡 Sugestões de Operações com Base nas Últimas 3 Horas")
df_operacoes, graficos_operacoes = sugestao_operacoes(ativos)
st.dataframe(df_operacoes, use_container_width=True)

# Exibir gráficos das sugestões
for nome, fig in graficos_operacoes.items():
    with st.expander(f"Visualização: {nome}"):
        st.pyplot(fig)

# Download de dados do ativo selecionado
dados = yf.download(tickers=ativo_codigo, start=inicio, end=fim, interval="3m")

df = dados[['Close']].copy()
df = df.rename(columns={"Close": "Preço (R$)"})
df["Horário"] = df.index

if not df.empty:
    entrada = df["Preço (R$)"].iloc[0]
    saida = df["Preço (R$)"].iloc[-1]
    lucro = saida - entrada

    st.line_chart(df.set_index("Horário"))

    col1, col2, col3 = st.columns(3)
    col1.metric("Lucro Simulado", f"R$ {lucro:.2f}", delta=f"{lucro/entrada*100:.2f}%")
    col2.metric("Preço Inicial", f"R$ {entrada:.2f}")
    col3.metric("Preço Atual", f"R$ {saida:.2f}")

    st.markdown("---")
    st.subheader("📊 Histórico de Preços (últimas 3h)")
    st.dataframe(df[::-1], use_container_width=True)
else:
    st.warning("⚠️ Nenhum dado encontrado para o ativo selecionado no intervalo de tempo escolhido.")

st.markdown("""
<div style='text-align:center'>
    <small>Atualizado em: {}</small>
</div>
""".format(datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")), unsafe_allow_html=True)


