# trading_bot/scripts/download_ohlcv.py

import pandas as pd
import requests
import os
from datetime import datetime

BASE_URL = "https://api.binance.com/api/v3/klines"
SAVE_FOLDER = "data"

BINANCE_INTERVALS = {
    "1m": "1m",
    "5m": "5m",
    "15m": "15m",
    "30m": "30m",
    "1H": "1h",
    "2H": "2h",
    "4H": "4h",
    "6H": "6h",
    "12H": "12h",
    "1D": "1d",
    "1W": "1w"
}

def download_ohlcv(symbol="BTCUSDT", interval="1D", limit=1000):
    print(f"📥 Descargando {limit} velas de {symbol} ({interval})...")

    interval_binance = BINANCE_INTERVALS.get(interval)
    if not interval_binance:
        raise ValueError(f"Intervalo no soportado: {interval}")

    params = {
        "symbol": symbol,
        "interval": interval_binance,
        "limit": limit
    }

    response = requests.get(BASE_URL, params=params)
    if response.status_code != 200:
        raise Exception(f"❌ Error en la API: {response.status_code} - {response.text}")

    data = response.json()
    columns = [
        "datetime", "open", "high", "low", "close", "volume",
        "close_time", "quote_asset_volume", "num_trades",
        "taker_buy_base", "taker_buy_quote", "ignore"
    ]

    df = pd.DataFrame(data, columns=columns)
    df["datetime"] = pd.to_datetime(df["datetime"], unit="ms")
    df = df[["datetime", "open", "high", "low", "close", "volume"]].copy()
    df = df.astype({"open": float, "high": float, "low": float, "close": float, "volume": float})

    filename = os.path.join(SAVE_FOLDER, f"{symbol}_{interval}.csv")
    os.makedirs(SAVE_FOLDER, exist_ok=True)
    df.to_csv(filename, index=False)
    print(f"✅ Datos guardados en {filename}")

if __name__ == "__main__":
    # Personaliza estos valores si lo ejecutas directamente
    download_ohlcv(symbol="BTCUSDT", interval="1D", limit=1000)
    download_ohlcv(symbol="BTCUSDT", interval="30m", limit=1000)
