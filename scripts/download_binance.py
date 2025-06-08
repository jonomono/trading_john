# trading_bot/scripts/download_binance.py

import pandas as pd
import requests
import os
import time
from datetime import datetime

BASE_URL = "https://api.binance.com/api/v3/klines"
SAVE_FOLDER = "data"
MASTER_FILE = os.path.join(SAVE_FOLDER, "all_data.csv")

BINANCE_INTERVALS = {
    "1m": "1m", "5m": "5m", "15m": "15m", "30m": "30m",
    "1H": "1h", "2H": "2h", "4H": "4h", "6H": "6h",
    "12H": "12h", "1D": "1d", "1W": "1w"
}

def download_ohlcv(symbol="BTCUSDT", interval="1D", limit=1000, append_to_master=False):
    interval_binance = BINANCE_INTERVALS.get(interval)
    if not interval_binance:
        raise ValueError(f"Intervalo no soportado: {interval}")

    all_data = []
    max_limit = 1000
    downloaded = 0
    end_time = int(datetime.utcnow().timestamp() * 1000)

    while downloaded < limit:
        current_limit = min(max_limit, limit - downloaded)

        params = {
            "symbol": symbol,
            "interval": interval_binance,
            "limit": current_limit,
            "endTime": end_time
        }

        response = requests.get(BASE_URL, params=params)
        if response.status_code != 200:
            raise Exception(f"Error de Binance API: {response.status_code} - {response.text}")

        data = response.json()
        if not data:
            break

        all_data.extend(data)
        downloaded += len(data)
        end_time = data[0][0] - 1
        time.sleep(0.5)

    df = pd.DataFrame(all_data, columns=[
        "datetime", "open", "high", "low", "close", "volume",
        "close_time", "quote_volume", "num_trades",
        "taker_buy_base", "taker_buy_quote", "ignore"
    ])

    df["datetime"] = pd.to_datetime(df["datetime"], unit="ms")
    df = df[["datetime", "open", "high", "low", "close", "volume"]].copy()

    for col in ["open", "high", "low", "close", "volume"]:
        df[col] = df[col].astype(float)

    df = df.sort_values("datetime")
    df.insert(0, "symbol", symbol)
    df.insert(1, "interval", interval)

    os.makedirs(SAVE_FOLDER, exist_ok=True)

    if append_to_master:
        if os.path.exists(MASTER_FILE):
            df.to_csv(MASTER_FILE, mode="a", header=False, index=False)
        else:
            df.to_csv(MASTER_FILE, index=False)
        return MASTER_FILE
    else:
        filename = os.path.join(SAVE_FOLDER, f"{symbol}_{interval}.csv")
        df.to_csv(filename, index=False)
        return filename
