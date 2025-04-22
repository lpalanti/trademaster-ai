import streamlit as st
import pandas as pd
import yfinance as yf
import datetime
import matplotlib.pyplot as plt
import mplfinance as mpf

# --- Configurações iniciais ---
st.set_page_config(page_title="TradeMasterAI", layout="wide")
st.markdown("""
    <style>
    body, .stApp, .css-18e3th9 {background-color: black; color: white;}
    .stDataFrame, .stMetric {background-color: #111; color: white;}
    .css-1d391kg input {background-color: #333; color: white;}
    </style>
""", unsafe_allow_html=True)

st.title("📈 TradeMasterAI - Painel de Simulação Day Trade")
st.markdown("Dados reais dos ativos | Atualiza a cada 3 minutos")

# --- Lista de ativos e período ---
ativos = {
    "Bitcoin (BTC-USD)": "BTC-USD",
    "Mini Índice (WIN=F)": "WIN=F",
    "Petrobras (PETR4.SA)": "PETR4.SA",
    "Vale (VALE3.SA)": "VALE3.SA",
    "Apple (AAPL)": "AAPL",
    "Tesla (TSLA)": "TSLA"
}
ativo_nome = st.selectbox("Selecione o ativo:", list(ativos.keys()))
ativo_codigo = ativos[ativo_nome]

# Escolha de período dinâmico
periodo = st.selectbox("Período de análise:", ["1h","3h","6h","12h"])
horas = int(periodo.replace("h",""))
fim = datetime.datetime.now()
inicio = fim - datetime.timedelta(hours=horas)

# --- Função para baixar dados com cache e tratamento de erro ---
@st.cache_data(show_spinner=False)
def obter_dados(codigo, start, end, interval="3m"):
    try:
        df = yf.download(tickers=codigo, start=start, end=end, interval=interval)
        return df
    except Exception:
        return pd.DataFrame()

# --- Aba de Sugestões de Operações ---
tab1, tab2 = st.tabs(["💡 Sugestões", "🛠 Simulação & Backtest"])
with tab1:
    st.subheader(f"Sugestões de Compra/Venda ({periodo})")
    df_all = []
    figs = {}
    for nome, cod in ativos.items():
        dados = obter_dados(cod, inicio, fim)
        if dados.empty:
            continue
        prec_min = float(dados["Close"].min())
        prec_max = float(dados["Close"].max())
        prec_atual = float(dados["Close"].iloc[-1])
        pot = (prec_max - prec_atual) / prec_atual * 100

        df_all.append({
            "Ativo": nome,
            "Preço Ideal 🟢": f"R$ {prec_min:.2f}",
            "Preço Ideal 🔴": f"R$ {prec_max:.2f}",
            "Atual ⚪": f"R$ {prec_atual:.2f}",
            "Potencial (%)": f"{pot:.2f}%"
        })

        # gráfico de barras
        fig, ax = plt.subplots()
        bars = ax.bar(
            ["Compra","Venda","Atual"],
            [prec_min,prec_max,prec_atual],
            color=["#4CAF50","#F44336","#9E9E9E"]
        )
        ax.bar_label(bars, fmt="R$ %.2f")
        ax.set_title(nome, color="white")
        ax.set_ylabel("Preço (R$)", color="white")
        ax.tick_params(colors="white")
        figs[nome] = fig

    df_sug = pd.DataFrame(df_all)
    st.dataframe(df_sug, use_container_width=True)

    for nm, fg in figs.items():
        with st.expander(f"Gráfico: {nm}"):
            st.pyplot(fg)

with tab2:
    st.subheader(f"Simulação & Backtest ({periodo})")

    # Simulação básica: compra na abertura do período e venda no fechamento
    df = obter_dados(ativo_codigo, inicio, fim)
    # Garante valores numéricos
    if not df.empty:
        entry = float(df["Close"].iloc[0])
        exit_price = float(df["Close"].iloc[-1])
    else:
        entry = 0.0
        exit_price = 0.0
    pnl = exit_price - entry

    # Backtest últimas 24h: compra no min, venda no max
    inicio24 = fim - datetime.timedelta(hours=24)
    df24 = obter_dados(ativo_codigo, inicio24, fim, interval="15m")
    if not df24.empty:
        min24 = float(df24["Close"].min())
        max24 = float(df24["Close"].max())
    else:
        min24 = max24 = 0.0
    pnl24 = max24 - min24

    # Monta histórico de trades
    historico = [
        {"Período":"Simulado","Entry (R$)":entry,"Exit (R$)":exit_price,"P&L (R$)":pnl},
        {"Período":"Backtest 24h","Entry (R$)":min24,"Exit (R$)":max24,"P&L (R$)":pnl24}
    ]
    hist_df = pd.DataFrame(historico)

    # Exibe métricas
    col1, col2 = st.columns(2)
    col1.metric("P&L Simulação", f"R$ {pnl:.2f}", delta=f"R$ {pnl:.2f}")
    col2.metric("P&L Backtest 24h", f"R$ {pnl24:.2f}", delta=f"R$ {pnl24:.2f}")

    st.markdown("**Histórico de Trades**")
    st.dataframe(hist_df, use_container_width=True)

    # Download CSV
    csv = hist_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Baixar histórico (CSV)",
        data=csv,
        file_name="trade_history.csv",
        mime="
