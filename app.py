import streamlit as st
import pandas as pd
import yfinance as yf
import datetime
import matplotlib.pyplot as plt
import mplfinance as mpf
import numpy as np

# Configuração da página
st.set_page_config(page_title="TradeMasterAI", layout="wide")

# Estilo preto e branco
st.markdown("""
    <style>
    body {background-color: black; color: white;}
    .stApp {background-color: black; color: white;}
    .css-18e3th9 {background-color: black; color: white;}
    .stDataFrame, .stMetric {background-color: #111; color: white;}
    .css-1d391kg input {background-color: #333; color: white;}
    </style>
""", unsafe_allow_html=True)

# Título\st.title("📈 TradeMasterAI - Painel de Simulação Day Trade")
st.markdown("**Dados reais dos ativos | Atualiza a cada 3 minutos**")

# Parâmetros de Simulação na barra lateral
st.sidebar.header("⚙️ Parâmetros de Simulação")
capital = st.sidebar.number_input("Capital Inicial (R$)", value=10000.0, step=1000.0)
leverage = st.sidebar.slider("Alavancagem", min_value=1, max_value=10, value=1)

# Seleção de ativos
ativos = {
    "Bitcoin (BTC-USD)": "BTC-USD",
    "Mini Índice (WIN=F)": "WIN=F",
    "Petrobras (PETR4.SA)": "PETR4.SA",
    "Vale (VALE3.SA)": "VALE3.SA",
    "Apple (AAPL)": "AAPL",
    "Tesla (TSLA)": "TSLA"
}
ativo_nome = st.selectbox("Selecione o ativo principal:", list(ativos.keys()))
ativo_codigo = ativos[ativo_nome]

# Seleção de período de análise para sugestões
periodos = {"1 hora":1, "3 horas":3, "6 horas":6, "12 horas":12}
periodo_nome = st.selectbox("Período de análise (h):", list(periodos.keys()), index=1)
periodo_horas = periodos[periodo_nome]

# Intervalos de tempo
fim = datetime.datetime.now()
inicio = fim - datetime.timedelta(hours=periodo_horas)

# Função cache para obter dados com tratamento de erros
def obter_dados(codigo, start, end, interval="3m"):
    try:
        df = yf.download(tickers=codigo, start=start, end=end, interval=interval)
        if df is None or df.empty:
            return pd.DataFrame()
        return df
    except Exception:
        return pd.DataFrame()

# Generating suggestions and charts
sugestoes = []
graficos = {}
for nome, codigo in ativos.items():
    dados = obter_dados(codigo, inicio, fim)
    if not dados.empty:
        minimo = dados['Close'].min()
        maximo = dados['Close'].max()
        atual = dados['Close'].iloc[-1]
        potencial = (maximo - minimo)/minimo*100
        sugestoes.append({
            "Ativo": nome,
            "Compra (R$)": f"{minimo:.2f}",
            "Venda (R$)": f"{maximo:.2f}",
            "Atual (R$)": f"{atual:.2f}",
            "% Potencial": f"{potencial:.2f}%"
        })
        # Gráfico de barras
        fig, ax = plt.subplots()
        barras = ax.bar(["Compra","Venda","Atual"], [minimo, maximo, atual], color=["#00B050","#F03C3C","#AAAAAA"])
        ax.set_title(nome)
        ax.set_ylabel("Preço (R$)")
        ax.bar_label(barras, fmt="%.2f")
        graficos[nome] = fig

# Exibir sugestões
st.subheader("💡 Sugestões de Operação (último período)")
if sugestoes:
    df_sug = pd.DataFrame(sugestoes)
    st.dataframe(df_sug, use_container_width=True)
else:
    st.warning("⚠️ Não foi possível obter sugestões, verifique o período ou a cotação dos ativos.")

# Exibir gráficos de sugestões
tab1, tab2 = st.tabs(["Sugestões", "Simulação 24h"])
with tab1:
    for nome, fig in graficos.items():
        with st.expander(f"Ver gráfico: {nome}"):
            st.pyplot(fig)

# Seção de Simulador de Operações (últimas 24h)
with tab2:
    st.subheader("🧮 Simulador de Operações - Últimas 24h")
    start_bt = fim - datetime.timedelta(hours=24)
    df_bt_list = []
    for nome, codigo in ativos.items():
        df_bt = obter_dados(codigo, start_bt, fim, interval="5m")
        if not df_bt.empty:
            entry = df_bt['Close'].min()
            exit_ = df_bt['Close'].max()
            qty = capital * leverage / entry
            pnl = (exit_ - entry) * qty
            df_bt_list.append({
                "Ativo": nome,
                "Entry (R$)": f"{entry:.2f}",
                "Exit (R$)": f"{exit_:.2f}",
                "Qty": f"{qty:.2f}",
                "PnL (R$)": f"{pnl:.2f}"  
            })
    if df_bt_list:
        df_bt = pd.DataFrame(df_bt_list)
        total_pnl = df_bt['PnL (R$)'].astype(float).sum()
        capital_final = capital + total_pnl
        col1, col2 = st.columns(2)
        col1.metric("Capital Inicial", f"R$ {capital:.2f}")
        col2.metric("Capital Final (Simulado)", f"R$ {capital_final:.2f}", delta=f"R$ {total_pnl:.2f}")
        st.dataframe(df_bt, use_container_width=True)
        # Backtest gráfico
        df_bt['% PnL'] = (df_bt['PnL (R$)'].astype(float) / capital) * 100
        st.bar_chart(df_bt.set_index('Ativo')['% PnL'])
        # Download do histórico completo
        csv = df_bt.to_csv(index=False).encode('utf-8')
        st.download_button(label="📥 Baixar histórico (CSV)", data=csv, file_name="historico_trades.csv", mime='text/csv')
    else:
        st.warning("⚠️ Não há dados para simular operações nas últimas 24h.")

# Data de atualização
st.markdown(f"<div style='text-align:center'><small>Atualizado em: {fim.strftime('%d/%m/%Y %H:%M:%S')}</small></div>", unsafe_allow_html=True)

