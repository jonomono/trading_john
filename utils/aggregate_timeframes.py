# trading_bot/utils/aggregate_timeframes.py

import pandas as pd
import os

def aggregate_timeframe(df: pd.DataFrame, rule: str) -> pd.DataFrame:
    """
    Agrega un DataFrame de velas 1H a un timeframe mayor (4H, 8H, 12H).

    :param df: DataFrame original con velas 1H
    :param rule: Regla de resampleo de pandas ('4H', '8H', '12H')
    :return: DataFrame con velas agregadas
    """
    df['datetime'] = pd.to_datetime(df['datetime'])
    df.set_index('datetime', inplace=True)

    ohlc_dict = {
        'open': 'first',
        'high': 'max',
        'low': 'min',
        'close': 'last',
        'adj_close': 'last',
        'volume': 'sum'
    }

    resampled = df.resample(rule).apply(ohlc_dict).dropna()
    resampled.reset_index(inplace=True)

    return resampled


def aggregate_and_save(symbol: str, base_interval: str, new_interval: str):
    """
    Agrega un archivo CSV con velas 1H y lo guarda en nuevo timeframe.

    :param symbol: Ticker base, ej. 'BTC-USD'
    :param base_interval: Intervalo original ('60m')
    :param new_interval: Intervalo nuevo ('4H', '8H', '12H')
    """
    filename = f"data/{symbol.replace('-', '_')}_{base_interval}.csv"
    if not os.path.exists(filename):
        print(f"❌ No se encontró el archivo: {filename}")
        return

    df = pd.read_csv(filename)
    aggregated = aggregate_timeframe(df, new_interval)

    new_filename = f"data/{symbol.replace('-', '_')}_{new_interval}.csv"
    aggregated.to_csv(new_filename, index=False)
    print(f"✅ Guardado: {new_filename}")


# Uso directo
if __name__ == "__main__":
    for tf in ["4H", "8H", "12H"]:
        aggregate_and_save("BTC-USD", "60m", tf)
