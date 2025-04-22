import streamlit as st
import pandas as pd
import yfinance as yf
import datetime
import plotly.graph_objects as go

st.set_page_config(page_title="TradeMasterAI", layout="wide")

# Estilo escuro
st.markdown("""
    <style>
    body {background-color: black; color: white;}
    .stApp, .stDataFrame, .stMetric, .css-1d391kg input {
        background-color: #111;
        color: white;
    }
    </style>
""", unsafe_allow_html=True)

st.title("📈 TradeMasterAI - Painel de Simulação Day Trade")

# Filtro de período
periodo = st.selectbox("Selecione o período de análise:", ["1h", "3h", "6h", "12h"])
multiplicador = int(periodo.replace("h", ""))
fim = datetime.datetime.now()
inicio = fim - datetime.timedelta(hours=multiplicador)

# Ativos disponíveis
ativos = {
    "Bitcoin (BTC-USD)": "BTC-USD",
    "Mini Índice (WIN=F)": "WIN=F",
    "Petrobras (PETR4.SA)": "PETR4.SA",
    "Vale (VALE3.SA)": "VALE3.SA",
    "Apple (AAPL)": "AAPL",
    "Tesla (TSLA)": "TSLA"
}

# Botão de atualização
atualizar = st.button("🔄 Atualizar dados")

@st.cache_data(show_spinner=False)
def obter_dados(codigo, start, end, intervalo="3m"):
    dados = yf.download(tickers=codigo, start=start, end=end, interval=intervalo)
    return dados

historico_trades = []
ranking = []

# Análise por ativo
for nome, codigo in ativos.items():
    with st.expander(f"📊 {nome}"):
        if atualizar:
            st.experimental_rerun()

        dados = obter_dados(codigo, inicio, fim)

        if dados.empty:
            st.warning("Sem dados disponíveis.")
            continue

        dados["SMA_5"] = dados["Close"].rolling(5).mean()
        dados["SMA_10"] = dados["Close"].rolling(10).mean()

        preco_min = dados["Close"].min()
        preco_max = dados["Close"].max()
        preco_atual = dados["Close"].iloc[-1]
        volume_total = dados["Volume"].sum()

        st.metric("📉 Preço Atual", f"R$ {preco_atual:.2f}")
        st.metric("💹 Volume Total", f"{volume_total:,.0f}")

        fig = go.Figure()
        fig.add_trace(go.Candlestick(
            x=dados.index,
            open=dados["Open"],
            high=dados["High"],
            low=dados["Low"],
            close=dados["Close"],
            name="Candles"
        ))
        fig.add_trace(go.Scatter(x=dados.index, y=dados["SMA_5"], mode='lines', name='SMA 5', line=dict(color='orange')))
        fig.add_trace(go.Scatter(x=dados.index, y=dados["SMA_10"], mode='lines', name='SMA 10', line=dict(color='blue')))
        fig.update_layout(height=400, title=f"{nome} - Últimas {periodo}", xaxis_title="Horário", yaxis_title="Preço")

        st.plotly_chart(fig, use_container_width=True)

        if dados["SMA_5"].iloc[-2] < dados["SMA_10"].iloc[-2] and dados["SMA_5"].iloc[-1] > dados["SMA_10"].iloc[-1]:
            st.success("📈 Alerta: SMA 5 cruzou acima da SMA 10 (Sinal de Compra)")
        elif dados["SMA_5"].iloc[-2] > dados["SMA_10"].iloc[-2] and dados["SMA_5"].iloc[-1] < dados["SMA_10"].iloc[-1]:
            st.error("📉 Alerta: SMA 5 cruzou abaixo da SMA 10 (Sinal de Venda)")

        st.markdown("### 🎯 Simulador de Trade")
        capital = st.number_input(f"Capital disponível ({nome})", min_value=100.0, value=1000.0, key=f"capital_{codigo}")
        alavancagem = st.slider(f"Alavancagem ({nome})", 1, 10, 1, key=f"alav_{codigo}")
        preco_entrada = st.number_input(f"Preço de entrada ({nome})", value=float(preco_atual), key=f"entrada_{codigo}")
        preco_saida = st.number_input(f"Preço de saída ({nome})", value=float(preco_atual * 1.01), key=f"saida_{codigo}")

        quantidade = (capital * alavancagem) / preco_entrada
        lucro_total = (preco_saida - preco_entrada) * quantidade
        perc = (lucro_total / capital) * 100

        st.metric("💰 Lucro Simulado", f"R$ {lucro_total:.2f}", delta=f"{perc:.2f}%")

        historico_trades.append({
            "Ativo": nome,
            "Entrada (R$)": preco_entrada,
            "Saída (R$)": preco_saida,
            "Lucro (R$)": round(lucro_total, 2),
            "Lucro (%)": round(perc, 2)
        })

        desvio = (preco_atual - dados["SMA_10"].mean()) / dados["SMA_10"].mean()
        ranking.append({"Ativo": nome, "Desvio %": round(desvio * 100, 2)})

        st.download_button(
            label="📥 Baixar histórico CSV",
            data=dados.to_csv().encode('utf-8'),
            file_name=f"{codigo}_historico.csv",
            mime="text/csv"
        )

# Ranking de ativos por desvio
df_rank = pd.DataFrame(ranking).sort_values("Desvio %")
st.markdown("### 🧮 Ranking de Ativos por Desvio da Média")
st.dataframe(df_rank, use_container_width=True)

# Histórico de trades
df_hist = pd.DataFrame(historico_trades)
if not df_hist.empty:
    st.markdown("### 📜 Histórico de Trades Simulados")
    st.dataframe(df_hist, use_container_width=True)
    st.metric("📈 P&L Total", f"R$ {df_hist['Lucro (R$)'].sum():.2f}")

# Backtest de compra no fundo e venda no topo
st.markdown("### 🧪 Backtest de Estratégia (Últimas 24h)")
inicio_bt = fim - datetime.timedelta(hours=24)
resultados_bt = []

for nome, codigo in ativos.items():
    dados_bt = obter_dados(codigo, inicio_bt, fim)
    if dados_bt.empty:
        continue
    preco_fundo = dados_bt["Low"].min()
    preco_topo = dados_bt["High"].max()
    lucro_bt = preco_topo - preco_fundo
    perc_bt = (lucro_bt / preco_fundo) * 100
    resultados_bt.append({
        "Ativo": nome,
        "Fundo (R$)": round(preco_fundo, 2),
        "Topo (R$)": round(preco_topo, 2),
        "Lucro (R$)": round(lucro_bt, 2),
        "Lucro (%)": round(perc_bt, 2)
    })

st.dataframe(pd.DataFrame(resultados_bt), use_container_width=True)

# Rodapé
st.markdown(
    f"<div style='text-align:center'><small>Atualizado em: {fim.strftime('%d/%m/%Y %H:%M:%S')}</small></div>",
    unsafe_allow_html=True
)

