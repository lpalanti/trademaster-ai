import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

# Configurações iniciais da página
st.set_page_config(page_title="TradeMaster AI", layout="wide")
st.title("📈 TradeMaster AI")
st.markdown("Analise ativos em tempo real com sugestões inteligentes baseadas no desempenho recente do mercado.")

# Lista de ativos populares (pode personalizar)
ativos_default = ['AAPL', 'GOOG', 'MSFT', 'TSLA', 'AMZN', 'NVDA', 'PETR4.SA', 'VALE3.SA', 'ITUB4.SA']

# Entrada do usuário
st.sidebar.header("Configurações")
ativos_usuario = st.sidebar.text_input("Digite os ativos separados por vírgula", ', '.join(ativos_default))
ativos = [a.strip().upper() for a in ativos_usuario.split(',')]

# Tempo atual e recorte de 3 horas
agora = datetime.utcnow()
inicio = agora - timedelta(hours=3)

# Função para obter dados de cada ativo
def analisar_ativo(ticker):
    try:
        ativo = yf.Ticker(ticker)
        df = ativo.history(interval="5m", start=inicio, end=agora)
        df.dropna(inplace=True)
        preco_atual = df['Close'][-1]
        preco_max = df['High'].max()
        preco_min = df['Low'].min()
        variacao = ((df['Close'][-1] - df['Open'][0]) / df['Open'][0]) * 100

        return {
            'Ativo': ticker,
            'Preço Atual': round(preco_atual, 2),
            'Melhor Preço de Venda': round(preco_max, 2),
            'Melhor Preço de Compra': round(preco_min, 2),
            'Variação (%)': round(variacao, 2)
        }
    except Exception as e:
        return {
            'Ativo': ticker,
            'Erro': str(e)
        }

# Carregando dados
st.subheader("📊 Análise de Ativos - Últimas 3 Horas")
analises = []

with st.spinner("Buscando dados em tempo real..."):
    for ativo in ativos:
        resultado = analisar_ativo(ativo)
        analises.append(resultado)

# Criar DataFrame com os resultados
df_resultado = pd.DataFrame(analises)

# Garantir que a coluna 'Variação (%)' existe antes de filtrar
if 'Variação (%)' in df_resultado.columns:
    df_validos = df_resultado[df_resultado['Variação (%)'].notnull()]
else:
    df_validos = pd.DataFrame()

# Exibir tabela principal
st.dataframe(df_resultado, use_container_width=True)

# Sugestões de investimento com base na maior variação positiva
if not df_validos.empty:
    melhores = df_validos.sort_values(by='Variação (%)', ascending=False).head(3)

    st.subheader("🚀 Melhores oportunidades do momento")
    for i, row in melhores.iterrows():
        st.markdown(f"""
        ### {row['Ativo']}
        - 💵 Preço atual: R$ {row['Preço Atual']}
        - 🔼 Melhor venda: R$ {row['Melhor Preço de Venda']}
        - 🔽 Melhor compra: R$ {row['Melhor Preço de Compra']}
        - 📈 Variação nas últimas 3h: {row['Variação (%)']}%
        """)

else:
    st.warning("Nenhum dado válido encontrado. Verifique os símbolos ou tente novamente mais tarde.")

# Rodapé
st.markdown("---")
st.caption("Powered by Yahoo Finance • Desenvolvido com ❤️ por TradeMaster AI")

