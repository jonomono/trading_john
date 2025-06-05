# trading_bot/strategies/structure_analysis.py

import pandas as pd

def detect_structure(df: pd.DataFrame, window: int = 5):
    """
    Detecta puntos de swing (máximos y mínimos locales) en el gráfico.
    
    :param df: DataFrame con columnas 'datetime', 'high', 'low'
    :param window: Número de velas a izquierda y derecha para confirmar swing
    :return: df con columnas extra: is_hh, is_ll
    """
    df['is_hh'] = df['high'][(df['high'].shift(window) < df['high']) &
                             (df['high'].shift(-window) < df['high'])]

    df['is_ll'] = df['low'][(df['low'].shift(window) > df['low']) &
                            (df['low'].shift(-window) > df['low'])]

    return df


def classify_trend(structure_df: pd.DataFrame):
    """
    Clasifica la tendencia según la secuencia de HH/HL o LH/LL.
    
    :param structure_df: DataFrame con columnas 'datetime', 'is_hh', 'is_ll'
    :return: string: 'uptrend', 'downtrend', 'range'
    """
    swings = structure_df.dropna(subset=['is_hh', 'is_ll'], how='all').copy()
    swings = swings[['datetime', 'high', 'low', 'is_hh', 'is_ll']]

    highs = swings.dropna(subset=['is_hh'])
    lows = swings.dropna(subset=['is_ll'])

    if len(highs) < 2 or len(lows) < 2:
        return 'range'

    # Compara últimos dos HH y LL
    hh1, hh2 = highs.iloc[-2]['is_hh'], highs.iloc[-1]['is_hh']
    ll1, ll2 = lows.iloc[-2]['is_ll'], lows.iloc[-1]['is_ll']

    if hh2 > hh1 and ll2 > ll1:
        return 'uptrend'
    elif hh2 < hh1 and ll2 < ll1:
        return 'downtrend'
    else:
        return 'range'


# Ejemplo de uso
if __name__ == "__main__":
    df = pd.read_csv("data/BTC_USD_1d.csv")
    df = detect_structure(df, window=5)
    trend = classify_trend(df)
    print(f"📈 Tendencia detectada: {trend}")
