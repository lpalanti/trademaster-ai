import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="TradeMaster AI", layout="wide")
st.title("📈 TradeMaster AI")
st.subheader("Sugestões inteligentes de ativos com base nos dados do dia")

st.markdown("---")
st.markdown("🔍 *Informe os ativos que deseja analisar (ex: PETR4.SA, VALE3.SA, AAPL)*")

tickers_input = st.text_input("Ativos separados por vírgula", "PETR4.SA, VALE3.SA, AAPL")

if tickers_input:
    tickers = [t.strip().upper() for t in tickers_input.split(",")]
    
    agora = datetime.now()
    hoje = agora.strftime('%Y-%m-%d')

    @st.cache_data(ttl=300)
    def analisar_ativo(ticker):
        try:
            ativo = yf.Ticker(ticker)
            df = ativo.history(interval="15m", start=hoje)
            df.dropna(inplace=True)

            if df.empty or len(df) < 2:
                return {
                    'Ativo': ticker,
                    'Erro': 'Sem dados suficientes para análise'
                }

            preco_atual = df['Close'].iloc[-1]
            preco_max = df['High'].max()
            preco_min = df['Low'].min()
            variacao = ((df['Close'].iloc[-1] - df['Open'].iloc[0]) / df['Open'].iloc[0]) * 100

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

    with st.spinner("🔎 Analisando ativos..."):
        analises = [analisar_ativo(t) for t in tickers]
        df_resultado = pd.DataFrame(analises)

        if 'Variação (%)' in df_resultado.columns:
            df_validos = df_resultado[df_resultado['Variação (%)'].notnull()]
        else:
            df_validos = pd.DataFrame()

    st.markdown("---")
    
    if not df_validos.empty:
        st.success("✅ Ativos analisados com sucesso! Veja os resultados abaixo:")
        st.dataframe(df_validos.sort_values("Variação (%)", ascending=False), use_container_width=True)
    else:
        st.warning("⚠️ Não foi possível obter dados válidos para os ativos informados.")

    if 'Erro' in df_resultado.columns:
        erros = df_resultado[df_resultado['Erro'].notnull()]
        if not erros.empty:
            with st.expander("❌ Ativos com erro de carregamento"):
                st.dataframe(erros[['Ativo', 'Erro']])

