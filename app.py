import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
import requests
from datetime import datetime, timedelta

st.set_page_config(layout="wide")

st.title("TradeMaster AI 📈🤖")

# Lista dos 20 ativos com maior histórico de volatilidade
ativos = [
    "PETR4.SA", "VALE3.SA", "ITUB4.SA", "BBDC4.SA", "BBAS3.SA",
    "ABEV3.SA", "B3SA3.SA", "WEGE3.SA", "RENT3.SA", "MGLU3.SA",
    "GGBR4.SA", "CSNA3.SA", "PRIO3.SA", "LREN3.SA", "BRKM5.SA",
    "ELET3.SA", "BRFS3.SA", "HAPV3.SA", "IGTI11.SA", "YDUQ3.SA"
]

# Filtros de seleção
col1, col2 = st.columns([3, 1])
with col1:
    ativo = st.selectbox("Selecione um ativo", ativos)
with col2:
    periodo_label = st.selectbox("Período do gráfico", ["7 dias", "15 dias", "30 dias", "90 dias"])
dias = int(periodo_label.split()[0])

# Datas para busca
data_fim = datetime.today()
data_inicio = data_fim - timedelta(days=dias)

# Dados via Yahoo Finance
df = yf.download(ativo, start=data_inicio, end=data_fim)

if df.empty:
    st.error("Não foi possível carregar os dados do ativo selecionado.")
else:
    df["% Var"] = df["Close"].pct_change() * 100
    df["Sinal"] = df["% Var"].apply(lambda x: "🔺" if x > 0 else "🔻" if x < 0 else "⏺️")

    # Gráfico
    st.subheader(f"Gráfico de Candlestick - {ativo} ({periodo_label})")
    fig = go.Figure(data=[go.Candlestick(
        x=df.index,
        open=df['Open'],
        high=df['High'],
        low=df['Low'],
        close=df['Close'],
        increasing_line_color='green',
        decreasing_line_color='red'
    )])
    fig.update_layout(xaxis_rangeslider_visible=False, height=400)
    st.plotly_chart(fig, use_container_width=True)

    # Tabela
    st.subheader("Tabela de Variações")
    st.dataframe(df[["Open", "High", "Low", "Close", "Volume", "% Var", "Sinal"]].sort_index(ascending=False), height=400)

    # Lógica de alerta via Telegram
    TOKEN = "SUA_CHAVE_DO_BOT"
    CHAT_ID = "SEU_CHAT_ID"

    alerta = None
    # Verifica se há dados suficientes
    if len(df) >= 2 and df["Close"].notna().all():
    preco_inicio = df["Close"].iloc[0]
    preco_fim = df["Close"].iloc[-1]
    variacao_total = ((preco_fim / preco_inicio) - 1) * 100

    if variacao_total >= 10:
        alerta = f"🚨 {ativo} subiu {variacao_total:.2f}% nos últimos {dias} dias!"
    elif variacao_total <= -10:
        alerta = f"⚠️ {ativo} caiu {variacao_total:.2f}% nos últimos {dias} dias!"

    if variacao_total >= 10:
        alerta = f"🚨 {ativo} subiu {variacao_total:.2f}% nos últimos {dias} dias!"
    elif variacao_total <= -10:
        alerta = f"⚠️ {ativo} caiu {variacao_total:.2f}% nos últimos {dias} dias!"

    if alerta:
        st.warning(alerta)
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        payload = {"chat_id": CHAT_ID, "text": alerta}
        try:
            r = requests.post(url, data=payload)
            if r.status_code == 200:
                st.success("Alerta enviado para o Telegram!")
            else:
                st.error("Erro ao enviar alerta para o Telegram.")
        except Exception as e:
            st.error(f"Erro ao tentar enviar alerta: {e}")
