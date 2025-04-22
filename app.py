import pandas as pd
import requests
import streamlit as st

# Função para buscar os dados de mercado
def get_market_data(assets, asset_type="crypto"):
    url = f"https://api.example.com/{asset_type}"  # Altere para a URL correta da API
    response = requests.get(url, params={"assets": assets})
    
    if response.status_code == 200:
        data = response.json()
        df = pd.DataFrame([{
            "name": item["name"] if isinstance(item, dict) and "name" in item else item.get("symbol", "Desconhecido"),
            "symbol": item["symbol"].upper() if isinstance(item, dict) and "symbol" in item else "Desconhecido",
            "volatility": abs(item.get("price_change_percentage_24h", 0)) if isinstance(item, dict) else 0,
            "price": item.get("current_price") if isinstance(item, dict) else 0
        } for item in data])
        return df
    else:
        return pd.DataFrame()  # Retorna um DataFrame vazio em caso de erro

# Função para exibir painel de criptomoedas
def crypto_panel():
    st.title("📉 Painel de Criptomoedas")

    # Lista de criptomoedas com ativos específicos
    crypto_assets = [
        "BTC", "ETH", "DOGE", "XRP", "ADA", "SOL", "MATIC", "LTC", "DOT", "LINK", "XLM", "UNI",
        "VET", "THETA", "SHIB", "AVAX", "ALGO", "FIL", "MANA", "HBAR"
    ]
    crypto_df = get_market_data(crypto_assets, asset_type="crypto")

    if not crypto_df.empty:
        crypto_df_sorted = crypto_df.sort_values("volatility", ascending=False)
        st.write("🔍 Criptomoedas mais voláteis:", crypto_df_sorted)
    else:
        st.error("Não foi possível carregar os dados das criptomoedas.")

# Função para exibir painel de ações
def stock_panel():
    st.title("📊 Painel de Ações")

    # Lista de ações com ativos específicos
    stock_assets = [
        "AAPL", "GOOG", "AMZN", "TSLA", "MSFT", "META", "NVDA", "NFLX", "BABA", "JPM", "DIS", "KO",
        "WMT", "MCD", "XOM", "BA", "INTC", "F", "PEP", "CSCO"
    ]
    stock_df = get_market_data(stock_assets, asset_type="stock")

    if not stock_df.empty:
        stock_df_sorted = stock_df.sort_values("volatility", ascending=False)
        st.write("📈 Ações mais voláteis:", stock_df_sorted)
    else:
        st.error("Não foi possível carregar os dados das ações.")

# Função principal que alterna entre os painéis
def main():
    st.sidebar.title("Navegação")
    option = st.sidebar.selectbox(
        "Escolha o painel:",
        ("Criptomoedas", "Ações")
    )

    if option == "Criptomoedas":
        crypto_panel()
    elif option == "Ações":
        stock_panel()

if __name__ == "__main__":
    main()

    elif option == "Ações":
        stock_panel()

if __name__ == "__main__":
    main()
