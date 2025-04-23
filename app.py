import streamlit as st
import pandas as pd
import yfinance as yf

st.set_page_config(page_title="TradeMaster AI", layout="wide")

st.title("📈 TradeMaster AI")

# Lista de ativos com maior histórico de volatilidade (exemplo)
ativos = [
    "PETR4.SA", "VALE3.SA", "ITUB4.SA", "BBDC4.SA", "BBAS3.SA",
    "ABEV3.SA", "WEGE3.SA", "MGLU3.SA", "LREN3.SA", "B3SA3.SA",
    "JBSS3.SA", "GGBR4.SA", "RENT3.SA", "CSNA3.SA", "RAIL3.SA",
    "PRIO3.SA", "BRKM5.SA", "UGPA3.SA", "SUZB3.SA", "EMBR3.SA"
]

# Sidebar
st.sidebar.header("Configurações")
ativo_selecionado = st.sidebar.selectbox("Selecione o ativo", ativos)

periodo = st.sidebar.selectbox(
    "Período de análise",
    ("7d", "15d", "30d", "90d", "180d", "1y"),
    index=2
)

st.sidebar.markdown("---")
st.sidebar.markdown("Desenvolvido por TradeMaster AI")

# Função para carregar dados
@st.cache_data
def carregar_dados(ticker, periodo):
    return yf.download(ticker, period=periodo)

df = carregar_dados(ativo_selecionado, periodo)

if not df.empty:
    preco_atual = df["Close"].iloc[-1]
    preco_inicial = df["Close"].iloc[0]
    variacao_total = ((preco_atual - preco_inicial) / preco_inicial) * 100

    col1, col2, col3 = st.columns(3)

    col1.metric("Ativo", ativo_selecionado)
    col2.metric("Preço Atual", f"R$ {preco_atual:.2f}")
    col3.metric("Variação no Período", f"{variacao_total:.2f}%", delta_color="inverse")

    if variacao_total >= 10:
        st.success("📈 Tendência de alta detectada!")
    elif variacao_total <= -10:
        st.error("📉 Tendência de baixa detectada!")
    else:
        st.warning("⚠️ Variação lateral ou indefinida.")
else:
    st.error("Não foi possível carregar os dados. Verifique o ativo ou o período.")
