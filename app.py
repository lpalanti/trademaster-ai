import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta

st.set_page_config(page_title="TradeMaster AI", layout="wide")

st.title("📈 TradeMaster AI")

ativos = [
    "PETR4.SA", "VALE3.SA", "ITUB4.SA", "BBDC4.SA", "ABEV3.SA",
    "BBAS3.SA", "WEGE3.SA", "MGLU3.SA", "LREN3.SA", "B3SA3.SA",
    "CSNA3.SA", "USIM5.SA", "GGBR4.SA", "JBSS3.SA", "BRFS3.SA",
    "PRIO3.SA", "ELET3.SA", "CMIG4.SA", "RAIL3.SA", "SUZB3.SA"
]

ativo = st.selectbox("Selecione um ativo", ativos)

periodo = st.selectbox("Selecione o período", ["7 dias", "15 dias", "30 dias", "90 dias", "180 dias", "1 ano"])
dias = int(periodo.split()[0])
data_inicial = datetime.now() - timedelta(days=dias)

df = yf.download(ativo, start=data_inicial)

# Verificação e exibição do DataFrame
if df.empty or "Close" not in df.columns:
    st.warning("Dados indisponíveis para esse período.")
else:
    st.subheader(f"Histórico de preços - {ativo}")
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df["Close"], mode="lines", name="Fechamento"))
    fig.update_layout(
        xaxis_title="Data",
        yaxis_title="Preço de Fechamento (R$)",
        title=f"{ativo} - Últimos {dias} dias",
        height=500
    )
    st.plotly_chart(fig, use_container_width=True)

    alerta = None
    if len(df) >= 2 and df["Close"].notna().all():
        preco_inicio = df["Close"].iloc[0]
        preco_fim = df["Close"].iloc[-1]
        variacao_total = ((preco_fim / preco_inicio) - 1) * 100

        if variacao_total >= 10:
            alerta = f"🚨 {ativo} subiu {variacao_total:.2f}% nos últimos {dias} dias!"
        elif variacao_total <= -10:
            alerta = f"⚠️ {ativo} caiu {variacao_total:.2f}% nos últimos {dias} dias!"
    
    if alerta:
        st.markdown(f"### {alerta}")

