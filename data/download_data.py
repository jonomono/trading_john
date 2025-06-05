# trading_bot/data/download_data.py

import yfinance as yf
import pandas as pd
import os

def download_data(symbol: str, interval: str, start: str, end: str):
    """
    Descarga datos históricos de yfinance y guarda en CSV.

    :param symbol: Ticker (ej. 'BTC-USD', 'ETH-USD', 'AAPL')
    :param interval: Intervalo ('1d', '1h', '30m')
    :param start: Fecha inicio (formato 'YYYY-MM-DD')
    :param end: Fecha fin (formato 'YYYY-MM-DD')
    """
    print(f"Descargando {symbol} en {interval} desde {start} hasta {end}")
    df = yf.download(tickers=symbol, interval=interval, start=start, end=end)
    
    if df.empty:
        print("⚠️ No se han encontrado datos para los parámetros indicados.")
        return

    df.dropna(inplace=True)
    df.reset_index(inplace=True)
    df.columns = [col.lower().replace(' ', '_') for col in df.columns]  # nombres consistentes

    # Guarda el CSV en la carpeta /data
    filename = f"data/{symbol.replace('-', '_')}_{interval}.csv"
    os.makedirs("data", exist_ok=True)
    df.to_csv(filename, index=False)
    print(f"✅ Datos guardados en {filename}")


# Ejemplo de uso
if __name__ == "__main__":
    download_data(
        symbol="BTC-USD",
        interval="30m",
        start="2023-01-01",
        end="2023-12-31"
    )
