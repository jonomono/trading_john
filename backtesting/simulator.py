# trading_bot/backtesting/simulator.py

import pandas as pd

def simulate_trade(entry, df, max_risk_reward=2.0):
    """
    Simula una operación long y evalúa si toca TP o SL.
    
    :param entry: Diccionario con datos de entrada (datetime, entry_price, sl)
    :param df: DataFrame completo de 30m velas (ordenado por datetime)
    :param max_risk_reward: Objetivo de R (ej: 2.0 para TP en 2R)
    :return: Diccionario con resultado
    """
    entry_price = entry["entry_price"]
    sl = entry["sl"]
    risk = entry_price - sl
    tp = entry_price + risk * max_risk_reward
    entry_time = pd.to_datetime(entry["datetime"])

    # Filtrar velas posteriores a la entrada
    df_future = df[df['datetime'] > entry_time].copy()

    for _, row in df_future.iterrows():
        low = row['low']
        high = row['high']

        if low <= sl:
            return {
                **entry,
                "exit_price": sl,
                "exit_time": row['datetime'],
                "result": "loss",
                "r_multiple": -1
            }
        elif high >= tp:
            return {
                **entry,
                "exit_price": tp,
                "exit_time": row['datetime'],
                "result": "win",
                "r_multiple": max_risk_reward
            }

    # Si no se ejecuta ni TP ni SL, cerramos al último close
    last = df_future.iloc[-1]
    final_r = (last['close'] - entry_price) / risk

    return {
        **entry,
        "exit_price": last['close'],
        "exit_time": last['datetime'],
        "result": "open",
        "r_multiple": round(final_r, 2)
    }


def backtest(entries, df_30m):
    """
    Simula todas las entradas sobre las velas 30m.
    
    :param entries: Lista de entradas detectadas
    :param df_30m: DataFrame completo de velas 30min
    :return: DataFrame con resultados de todas las operaciones
    """
    results = [simulate_trade(entry, df_30m) for entry in entries]
    return pd.DataFrame(results)


# Ejemplo de uso
if __name__ == "__main__":
    from strategies.entry_logic import find_entry_signals

    df = pd.read_csv("data/BTC_USD_30m.csv")
    df['datetime'] = pd.to_datetime(df['datetime'])

    entries = find_entry_signals(df, "uptrend")
    result_df = backtest(entries, df)

    print(result_df[['datetime', 'entry_price', 'exit_price', 'result', 'r_multiple']].head())
    result_df.to_csv("logs/backtest_results.csv", index=False)
    print("✅ Log guardado en logs/backtest_results.csv")
