# trading_bot/strategies/retest_entry.py

import pandas as pd

def find_breakout_levels(df: pd.DataFrame, window: int = 20):
    """
    Detecta niveles de resistencia (máximos anteriores) para posibles rupturas.
    
    :param df: DataFrame de velas
    :param window: Número de velas para buscar máximos locales
    :return: Lista de niveles de ruptura (precios)
    """
    breakout_levels = []
    highs = df['high'].rolling(window=window).max()

    for i in range(window, len(df)):
        prev_high = highs[i - 1]
        curr_close = df.iloc[i]['close']
        if curr_close > prev_high and prev_high not in breakout_levels:
            breakout_levels.append(prev_high)

    return breakout_levels


def is_bullish_confirmation(candle_prev, candle_curr):
    return (
        candle_prev['close'] < candle_prev['open'] and
        candle_curr['close'] > candle_curr['open'] and
        candle_curr['close'] > candle_prev['open'] and
        candle_curr['open'] <= candle_prev['close']
    )


def find_retest_entries(df: pd.DataFrame, higher_tf_trend: str):
    """
    Busca entradas tipo ruptura + retest en gráfico 30m
    
    :param df: DataFrame 30min
    :param higher_tf_trend: 'uptrend', etc.
    :return: lista de entradas (dict)
    """
    entries = []
    levels = find_breakout_levels(df, window=20)

    for i in range(2, len(df)):
        prev = df.iloc[i - 1]
        curr = df.iloc[i]

        if higher_tf_trend != 'uptrend':
            continue

        for lvl in levels:
            # Retest: precio baja cerca del nivel y luego sube con vela fuerte
            if abs(curr['low'] - lvl) / lvl < 0.005:  # tolerancia < 0.5%
                if is_bullish_confirmation(prev, curr):
                    entry = {
                        "datetime": curr['datetime'],
                        "entry_price": curr['close'],
                        "sl": curr['low'],  # SL bajo vela retest
                        "reason": f"retest + breakout lvl {round(lvl, 2)}"
                    }
                    entries.append(entry)
                    break  # evita múltiples entradas en misma vela

    return entries


# Ejemplo de uso
if __name__ == "__main__":
    df = pd.read_csv("data/BTC_USD_30m.csv")
    df['datetime'] = pd.to_datetime(df['datetime'])

    trend = "uptrend"
    entries = find_retest_entries(df, trend)

    for e in entries[:5]:
        print(f"📌 Entrada detectada: {e}")
