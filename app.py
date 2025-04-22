import streamlit as st
import yfinance as yf
import pandas as pd
import time

# Função para obter os dados financeiros de um ativo
def obter_dados_ativos(ativos):
    dados = []
    for ativo in ativos:
        try:
            df = yf.download(ativo, period="1d", interval="5m")  # Obtém dados das últimas 3 horas
            df['Ativo'] = ativo  # Adiciona o nome do ativo
            dados.append(df)
            time.sleep(0.15)  # Aumento do tempo de espera entre as requisições para evitar rate limit
        except (yf.YFRateLimitError, yf.YFPricesMissingError) as e:
            st.warning(f"Erro ao obter dados de {ativo}: {e}")
            continue
    return dados

# Lista de 50 ativos populares
ativos_populares = [
    'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'NVDA', 'META', 'BRK-B', 'V', 'MA',
    'JPM', 'UNH', 'HD', 'DIS', 'PYPL', 'NFLX', 'BABA', 'INTC', 'AMD', 'BA',
    'CSCO', 'WMT', 'KO', 'PFE', 'VZ', 'PEP', 'ABT', 'MRK', 'CVX', 'XOM',
    'GS', 'C', 'JNJ', 'T', 'MCD', 'WFC', 'NKE', 'PG', 'ADBE', 'ORCL',
    'SBUX', 'TSM', 'GE', 'UPS', 'RTX', 'LMT', 'GM', 'X', 'CAT', 'GM',
    'LUV', 'UAL', 'SPY', 'IWM', 'QQQ', 'DIA'
]

# Divisão dos ativos em lotes (25 por vez)
lotes_ativos = [ativos_populares[i:i+25] for i in range(0, len(ativos_populares), 25)]

# Coleta os dados de todos os ativos
todos_dados = []
for lote in lotes_ativos:
    dados_lote = obter_dados_ativos(lote)
    todos_dados.extend(dados_lote)

# Concatena todos os dados coletados em um único DataFrame
df_resultado = pd.concat(todos_dados)

# Exibe o DataFrame com os dados
if not df_resultado.empty:
    st.write("Dados das Ações", df_resultado.tail())
else:
    st.write("Nenhum dado encontrado para os ativos selecionados.")

# Filtra os ativos válidos com base na variação
df_validos = df_resultado[df_resultado['Adj Close'].notnull()]
df_validos['Variação (%)'] = df_validos.groupby('Ativo')['Adj Close'].pct_change() * 100

# Exibe os ativos com a maior variação
ativos_com_maior_variacao = df_validos.groupby('Ativo')['Variação (%)'].last().sort_values(ascending=False).head(10)

# Exibe os ativos recomendados
st.write("Ativos com Maior Variação (%) nas Últimas 3 Horas", ativos_com_maior_variacao)

# Sugestão de compra e venda
ativos_com_maior_variacao_excluidos = ativos_com_maior_variacao.index.tolist()
df_validos = df_validos[df_validos['Ativo'].isin(ativos_com_maior_variacao_excluidos)]

# Função para calcular o preço de compra e venda
def obter_precos(df):
    precos = {}
    for ativo in df['Ativo'].unique():
        df_ativo = df[df['Ativo'] == ativo]
        preco_compra = df_ativo['Low'].min()  # Menor preço de venda
        preco_venda = df_ativo['High'].max()  # Maior preço de venda
        precos[ativo] = {'Compra': preco_compra, 'Venda': preco_venda}
    return precos

# Exibindo os preços de compra e venda
precos = obter_precos(df_validos)
st.write("Sugestões de Preço de Compra e Venda", precos)

# Exibe informações de cada ativo
st.write("Informações Detalhadas de Ativos")
for ativo, preco in precos.items():
    st.write(f"**{ativo}**: Compra: {preco['Compra']:.2f} | Venda: {preco['Venda']:.2f}")


