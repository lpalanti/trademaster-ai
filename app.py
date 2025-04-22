import streamlit as st
import pandas as pd
import numpy as np

# Função para gerar dados aleatórios (simulando os dados de ativos)
def gerar_dados_ativos():
    ativos = ['Bitcoin (BTC)', 'Ethereum (ETH)', 'Ripple (XRP)', 'Dogecoin (DOGE)', 'Litecoin (LTC)',
              'Cardano (ADA)', 'Polkadot (DOT)', 'Solana (SOL)', 'Avalanche (AVAX)', 'Chainlink (LINK)',
              'Shiba Inu (SHIB)', 'Binance Coin (BNB)', 'Polygon (MATIC)', 'Uniswap (UNI)', 'Terra (LUNA)']
    dados = []
    for ativo in ativos:
        volatilidade = np.random.uniform(1, 10)  # Volatilidade aleatória
        preco_min = np.random.uniform(10, 500)  # Preço mínimo aleatório
        preco_max = preco_min + np.random.uniform(10, 100)  # Preço máximo aleatório
        preco_compra = preco_min + (preco_max - preco_min) * np.random.uniform(0.2, 0.4)  # Preço ideal de compra
        preco_venda = preco_max - (preco_max - preco_min) * np.random.uniform(0.2, 0.4)  # Preço ideal de venda
        
        dados.append({
            'Ativo': ativo,
            'Volatilidade': f'{volatilidade:.2f}%',
            'Preço Mínimo': f'${preco_min:.2f}',
            'Preço Máximo': f'${preco_max:.2f}',
            'Preço Ideal de Compra': f'${preco_compra:.2f}',
            'Preço Ideal de Venda': f'${preco_venda:.2f}'
        })
    
    return pd.DataFrame(dados)

# Título da aplicação
st.title("Trademaster AI - Dashboard de Day Trade")

# Barra lateral para seleção de categorias
opcao = st.sidebar.selectbox(
    'Escolha uma categoria de ativos:',
    ['Cripto', 'Ações', 'Commodities']
)

# Exibindo os dados de acordo com a categoria escolhida
if opcao == 'Cripto':
    st.header("Ativos Cripto")
    ativos_cripto = gerar_dados_ativos()
    st.dataframe(ativos_cripto)

elif opcao == 'Ações':
    st.header("Ativos Ações")
    ativos_acoes = gerar_dados_ativos()
    st.dataframe(ativos_acoes)

elif opcao == 'Commodities':
    st.header("Ativos Commodities")
    ativos_commodities = gerar_dados_ativos()
    st.dataframe(ativos_commodities)

# Informações adicionais de como usar
st.sidebar.markdown("""
### Sobre:
- Este aplicativo exibe dados aleatórios de ativos em tempo real, com base nas categorias de Cripto, Ações e Commodities.
- Use os botões para navegar entre as categorias e visualizar informações como volatilidade, preços mínimos e máximos, e preços ideais de compra e venda.
""")
