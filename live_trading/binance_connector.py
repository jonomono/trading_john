# trading_bot/live_trading/binance_connector.py


from binance.client import Client
from dotenv import load_dotenv
import os

load_dotenv()  # Carga el archivo .env

def get_binance_client():
    api_key = os.getenv("BINANCE_API_KEY")
    api_secret = os.getenv("BINANCE_API_SECRET")

    if not api_key or not api_secret:
        raise Exception("❌ Claves API no definidas en .env")

    return Client(api_key, api_secret)


def get_balance(client, asset="USDT"):
    balances = client.get_asset_balance(asset=asset)
    return float(balances['free']) if balances else 0
