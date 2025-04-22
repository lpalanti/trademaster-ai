import streamlit as st
import pandas as pd
import yfinance as yf
import datetime

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



