# trading_bot/strategies/entry_logic.py

import pandas as pd

def is_bullish_engulfing(candle_prev, candle_curr):
    """
    Detecta vela envolvente alcista.
    """
    return (
        candle_prev['close'] < candle_prev['open'] and
        candle_curr['close'] > candle_curr['open'] and
        candle_curr['close'] > candle_prev['open'] and
        candle_curr['open'] < candle_prev['close']
    )


def find_entry_signals(df_30m: pd.DataFrame, higher_tf_trend: str):
    """
    Busca señales de entrada en 30m confirmando la tendencia de timeframes mayores.

    :param df_30m: DataFrame con velas de 30 minutos
    :param higher_tf_trend: 'uptrend', 'downtrend' o 'range'
    :return: Lista de operaciones candidatas
    """
    entries = []

    for i in range(1, len(df_30m)):
        prev = df_30m.iloc[i - 1]
        curr = df_30m.iloc[i]

        if higher_tf_trend == 'uptrend' and is_bullish_engulfing(prev, curr):
            entry = {
                "datetime": curr['datetime'],
                "entry_price": curr['close'],
                "sl": min(prev['low'], curr['low']),
                "reason": "bullish engulfing + uptrend"
            }
            entries.append(entry)

    return entries


# Ejemplo de uso
if __name__ == "__main__":
    df_30m = pd.read_csv("data/BTC_USD_30m.csv")
    df_30m['datetime'] = pd.to_datetime(df_30m['datetime'])

    # Suponiendo que ya analizamos y confirmamos tendencia alcista
    trend = "uptrend"

    signals = find_entry_signals(df_30m, trend)
    for s in signals[:5]:
        print(f"🚀 Entrada detectada: {s}")
