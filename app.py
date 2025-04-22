import streamlit as st
from streamlit_autorefresh import st_autorefresh
import pandas as pd
import random

# Atualiza a cada 3 minutos (180.000 ms)
st_autorefresh(interval=180000, key="refresh")

st.set_page_config(page_title="SIFUT | Day Trade", layout="wide")
st.title("SIFUT - Sistema de Informações para Day Trade")

# Botões de navegação
page = st.sidebar.radio("Escolha a área:", ["Cripto", "Ações", "Commodities"])

# Função para simular dados (você vai substituir por API real depois)
def gerar_dados(ativos):
    data = []
    for ativo in ativos:
        preco_min = round(random.uniform(10, 100), 2)
        preco_max = round(preco_min + random.uniform(5, 20), 2)
        preco_ideal_compra = round((preco_min + preco_max) / 2 - random.uniform(0.5, 2), 2)
        preco_ideal_venda = round((preco_min + preco_max) / 2 + random.uniform(0.5, 2), 2)
        volatilidade = round(preco_max - preco_min, 2)
        volatilidade_pct = round((volatilidade / preco_min) * 100, 2)

        data.append({
            "Ativo": ativo,
            "Volatilidade": volatilidade,
            "% Volatilidade": f"{volatilidade_pct}%",
            "Menor Preço": preco_min,
            "Maior Preço": preco_max,
            "Preço Ideal de Compra": preco_ideal_compra,
            "Preço Ideal de Venda": preco_ideal_venda,
        })
    return pd.DataFrame(data)

# Dicionário de ativos
ativos_dict = {
    "Cripto": [
        "Bitcoin (BTC)", "Ethereum (ETH)", "Ripple (XRP)", "Dogecoin (DOGE)", "Litecoin (LTC)", 
        "Cardano (ADA)", "Polkadot (DOT)", "Solana (SOL)", "Avalanche (AVAX)", "Chainlink (LINK)",
        "Shiba Inu (SHIB)", "Binance Coin (BNB)", "Polygon (MATIC)", "Uniswap (UNI)", "Terra (LUNA)"
    ],
    "Ações": [
        "Tesla (TSLA)", "Amazon (AMZN)", "Apple (AAPL)", "Meta (META)", "Netflix (NFLX)", "Nvidia (NVDA)",
        "GameStop (GME)", "AMC Entertainment (AMC)", "Spotify (SPOT)", "Palantir (PLTR)", "Roku (ROKU)",
        "Square (SQ)", "Zoom Video (ZM)", "DocuSign (DOCU)", "Beyond Meat (BYND)", "Coinbase (COIN)",
        "Robinhood (HOOD)", "Moderna (MRNA)", "Snowflake (SNOW)", "Spotify (SPOT)"
    ],
    "Commodities": [
        "Ouro (XAU/USD)", "Petróleo Brent", "Petróleo WTI", "Cobre (Copper)", "Algodão (Cotton)",
        "Café (Coffee)", "Soja (Soybeans)", "Milho (Corn)", "Açúcar (Sugar)", "Paládio (Palladium)"
    ]
}

# Gera dados para a página escolhida
df = gerar_dados(ativos_dict[page])

# Exibição dos dados
st.subheader(f"Painel de Monitoramento - {page}")
st.dataframe(df, use_container_width=True)
