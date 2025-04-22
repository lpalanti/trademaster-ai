import streamlit as st
import yfinance as yf
import pandas as pd

# Função para obter dados de mercado (cripto ou ações)
def get_market_data(assets, asset_type="crypto"):
    data = []
    
    for symbol in assets:
        try:
            if asset_type == "crypto":
                # Obtendo dados para criptos
                url = f"https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&ids={symbol}"
                response = requests.get(url).json()
                if response:
                    item = response[0]
                    data.append({
                        "name": item.get("name", item.get("symbol")),
                        "symbol": item.get("symbol").upper(),
                        "volatility": abs(item.get("price_change_percentage_24h", 0)),
                        "price": item.get("current_price", 0),
                        "low": item.get("low_24h", 0),
                        "high": item.get("high_24h", 0),
                        "buy_price": item.get("current_price", 0) * 0.98,  # Preço de compra sugerido
                        "sell_price": item.get("current_price", 0) * 1.02,  # Preço de venda sugerido
                    })
            elif asset_type == "stock":
                # Obtendo dados para ações
                stock_data = yf.Ticker(symbol).history(period="1d")
                if not stock_data.empty:
                    latest_data = stock_data.iloc[-1]
                    data.append({
                        "name": symbol.upper(),
                        "symbol": symbol.upper(),
                        "volatility": abs(latest_data['Close'] - latest_data['Open']),
                        "price": latest_data['Close'],
                        "low": latest_data['Low'],
                        "high": latest_data['High'],
                        "buy_price": latest_data['Close'] * 0.98,  # Preço de compra sugerido
                        "sell_price": latest_data['Close'] * 1.02,  # Preço de venda sugerido
                    })
        except Exception as e:
            st.error(f"Erro ao obter dados para {symbol}: {str(e)}")

    return pd.DataFrame(data)

# Lista de ativos para criptos e ações
cryptos = ['bitcoin', 'ethereum', 'ripple', 'dogecoin', 'litecoin']
stocks = ['TSLA', 'AMZN', 'AAPL', 'META', 'NFLX', 'NVDA', 'GME', 'AMC', 'SPOT', 'PLTR', 'ROKU', 'SQ', 'ZM', 'DOCU', 'BYND', 'COIN', 'HOOD', 'MRNA', 'SNOW']

# Interface do Streamlit
st.title("💹 Dashboard de Ativos Financeiros")

# Opções de visualização
option = st.selectbox("Escolha o tipo de ativo:", ("Criptomoedas", "Ações"))

# Painel de Criptomoedas
if option == "Criptomoedas":
    st.subheader("📊 Criptomoedas (últimas 24h)")
    crypto_df = get_market_data(cryptos, asset_type="crypto")
    if not crypto_df.empty:
        crypto_df_sorted = crypto_df.sort_values("volatility", ascending=False)
        st.dataframe(crypto_df_sorted[["name", "symbol", "price", "low", "high", "buy_price", "sell_price", "volatility"]])

# Painel de Ações
elif option == "Ações":
    st.subheader("📊 Ações (últimas 24h)")
    stock_df = get_market_data(stocks, asset_type="stock")
    if not stock_df.empty:
        stock_df_sorted = stock_df.sort_values("volatility", ascending=False)
        st.dataframe(stock_df_sorted[["name", "symbol", "price", "low", "high", "buy_price", "sell_price", "volatility"]])
