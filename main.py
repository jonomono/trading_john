# trading_bot/main.py

import pandas as pd
from strategies.structure_analysis import detect_structure, classify_trend
from strategies.entry_logic import find_entry_signals as engulfing_strategy
from strategies.retest_entry import find_retest_entries as retest_strategy
from backtesting.simulator import backtest
from backtesting.evaluator import evaluate_trades
from logs.logger import log_backtest_summary

def main(strategy_name="bullish_engulfing", r_target=2.0):
    print(f"\n🚀 Ejecutando backtest con estrategia: {strategy_name}")

    # 1. Cargar velas
    df_higher = pd.read_csv("data/BTC_USD_1d.csv")
    df_30m = pd.read_csv("data/BTC_USD_30m.csv")
    df_higher['datetime'] = pd.to_datetime(df_higher['datetime'])
    df_30m['datetime'] = pd.to_datetime(df_30m['datetime'])

    # 2. Detectar estructura/tendencia en timeframe mayor
    df_higher = detect_structure(df_higher, window=5)
    trend = classify_trend(df_higher)
    print(f"📈 Tendencia mayor detectada: {trend}")

    # 3. Detectar señales según estrategia
    if strategy_name == "bullish_engulfing":
        entries = engulfing_strategy(df_30m, trend)
    elif strategy_name == "retest_entry":
        entries = retest_strategy(df_30m, trend)
    else:
        print("❌ Estrategia no reconocida.")
        return

    if not entries:
        print("⚠️ No se detectaron entradas.")
        return

    # 4. Backtesting
    result_df = backtest(entries, df_30m)

    # 5. Evaluación
    metrics = evaluate_trades(result_df)

    # 6. Logging del resultado
    log_backtest_summary(
        strategy_name=strategy_name,
        timeframe="1D→30m",
        r_target=r_target,
        metrics=metrics,
        notes="Auto-backtest desde main.py"
    )

    # 7. Mostrar resumen
    print("\n✅ Resumen:")
    for k, v in metrics.items():
        print(f"{k}: {v}")


if __name__ == "__main__":
    # Cambia aquí la estrategia a testear: 'bullish_engulfing' o 'retest_entry'
    main(strategy_name="retest_entry", r_target=2.0)
