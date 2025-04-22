import streamlit as st
import pandas as pd
import yfinance as yf
import datetime
import matplotlib.pyplot as plt

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

st.title("📈 TradeMasterAI - Painel de Simulação Day Trade")
st.markdown("**Dados reais dos ativos | Atualiza a cada 3 minutos**")

# Seleção de ativos
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

# Seleção de período de análise
periodos = {"1 hora":1, "3 horas":3, "6 horas":6, "12 horas":12}
periodo_nome = st.selectbox("Selecionar período de análise:", list(periodos.keys()), index=1)
periodo_horas = periodos[periodo_nome]

# Definir intervalo de tempo
fim = datetime.datetime.now()
inicio = fim - datetime.timedelta(hours=periodo_horas)

# Função de sugestão com cache
@st.cache_data(show_spinner=False)
def obter_dados(codigo, start, end):
    df = yf.download(tickers=codigo, start=start, end=end, interval="3m")
    return df

# Coleta dados de todos os ativos para sugestões
sugestoes = []
graficos = {}
for nome, codigo in ativos.items():
    dados = obter_dados(codigo, inicio, fim)
    if not dados.empty:
        minimo = dados['Close'].min()
        maximo = dados['Close'].max()
        atual = dados['Close'].iloc[-1]
        sugestoes.append({
            "Ativo": nome,
            "Preço Compra": f"R$ {minimo:.2f}",
            "Preço Venda": f"R$ {maximo:.2f}",
            "Preço Atual": f"R$ {atual:.2f}",
            "% Potencial": f"{(maximo-minimo)/minimo*100:.2f}%"
        })
        # Gráfico de barras
        fig, ax = plt.subplots()
        barras = ax.bar(["Compra","Venda","Atual"], [minimo, maximo, atual], color=["#00B050","#F03C3C","#AAAAAA"])
        ax.set_title(nome)
        ax.set_ylabel("Preço (R$)")
        ax.bar_label(barras, fmt='%.2f')
        graficos[nome] = fig

# Exibir sugestões
st.subheader("💡 Sugestões de Operação (último período)")
df_sug = pd.DataFrame(sugestoes)
st.dataframe(df_sug, use_container_width=True)

# Notificações visuais para ativo selecionado
dados_ativo = obter_dados(ativo_codigo, inicio, fim)
if not dados_ativo.empty:
    preco_min = dados_ativo['Close'].min()
    preco_max = dados_ativo['Close'].max()
    preco_atual = dados_ativo['Close'].iloc[-1]
    if preco_atual <= preco_min:
        st.success(f"🔔 {ativo_nome} está no preço mais baixo do período: R$ {preco_atual:.2f}")
    if preco_atual >= preco_max:
        st.error(f"🔔 {ativo_nome} está no preço mais alto do período: R$ {preco_atual:.2f}")

# Exibir gráficos em expander
for nome, fig in graficos.items():
    with st.expander(f"Ver gráfico: {nome}"):
        st.pyplot(fig)

# Gráfico de linha com volume se disponível
st.markdown("---")
st.subheader(f"📈 Gráfico de Preço e Volume - {ativo_nome}")
if not dados_ativo.empty:
    df_plot = dados_ativo[['Close', 'Volume']].copy()
    df_plot = df_plot.rename(columns={'Close':'Preço (R$)', 'Volume':'Volume'})
    # Preço
    st.line_chart(df_plot['Preço (R$)'])
    # Volume
    st.bar_chart(df_plot['Volume'])
else:
    st.warning("⚠️ Não há dados para exibir o gráfico de volume.")

# Histórico de preços
st.markdown("---")
st.subheader(f"📊 Histórico de Preços (últimas {periodo_horas}h)")
if not dados_ativo.empty:
    df_hist = dados_ativo[['Close']].copy()
    df_hist = df_hist.rename(columns={'Close':'Preço (R$)'}).reset_index()
    df_hist['Horário'] = df_hist['Datetime']
    st.dataframe(df_hist[["Horário","Preço (R$)"]][::-1], use_container_width=True)
else:
    st.warning("⚠️ Nenhum dado encontrado no histórico.")

st.markdown(f"<div style='text-align:center'><small>Atualizado em: {fim.strftime('%d/%m/%Y %H:%M:%S')}</small></div>", unsafe_allow_html=True)



