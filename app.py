import streamlit as st
import pandas as pd
import numpy as np
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
st.markdown("Simulação com ativos BTC-USD, WIN=F e PETR4.SA | Atualiza a cada 3 minutos")

# Simulação de dados
np.random.seed(42)
data = pd.date_range(end=datetime.datetime.now(), periods=20, freq='3min')
saldo = np.cumsum(np.random.randn(20)) * 50 + 10000
ativos = ["BTC-USD", "WIN=F", "PETR4.SA"]
ativo = st.selectbox("Selecione o ativo para visualizar:", ativos)

df = pd.DataFrame({
    "Horário": data,
    "Saldo Simulado (R$)": saldo
})

st.line_chart(df.set_index("Horário"))

col1, col2, col3 = st.columns(3)
col1.metric("Lucro do Dia", f"R$ {df['Saldo Simulado (R$)'].iloc[-1] - df['Saldo Simulado (R$)'].iloc[0]:.2f}")
col2.metric("Total de Trades", "15")
col3.metric("Taxa de Acerto", "73%")

st.markdown("---")
st.subheader("📊 Histórico de Resultados")
st.dataframe(df[::-1], use_container_width=True)
