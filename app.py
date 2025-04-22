import streamlit as st
import requests

st.set_page_config(page_title="TradeMaster AI", layout="wide")

st.title("📊 TradeMaster AI – Assistente Cripto")

# Seleção de criptomoeda
coin = st.selectbox("Escolha a Criptomoeda:", ["bitcoin", "ethereum", "solana", "dogecoin"])

# Consulta de preço atual
url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin}&vs_currencies=usd"
r = requests.get(url)
data = r.json()

# Exibição do preço
price = data[coin]["usd"]
st.metric(label=f"Preço do {coin.capitalize()}", value=f"${price}")
