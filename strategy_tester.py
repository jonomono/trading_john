# trading_bot/strategy_tester.py

import pandas as pd
from strategies.structure_analysis import detect_structure, classify_trend
from strategies.entry_logic import find_entry_signals as engulfing_strategy
from strategies.retest_entry import find_retest_entries as retest_strategy
from backtesting.simulator import backtest
from backtesting.evaluator import evaluate_trades
from logs.logger import log_backtest_summary

def run_test(strategy_name, higher_tf, r_target):
    print(f"\n▶️ Testeando: {strategy_name} | TF mayor: {higher_tf} | R objetivo: {r_target}")

    # 1. Cargar datos
    df_tf = pd.read_csv(f"data/BTC_USD_{higher_tf}.csv")
    df_30m = pd.read_csv("data/BTC_USD_30m.csv")
    df_tf['datetime'] = pd.to_datetime(df_tf['datetime'])
    df_30m['datetime'] = pd.to_datetime(df_30m['datetime'])

    # 2. Detectar estructura
    df_tf = detect_structure(df_tf, window=5)
    trend = classify_trend(df_tf)

    # 3. Detectar señales
    if strategy_name == "bullish_engulfing":
        entries = engulfing_strategy(df_30m, trend)
    elif strategy_name == "retest_entry":
        entries = retest_strategy(df_30m, trend)
    else:
        print("❌ Estrategia no válida")
        return

    if not entries:
        print("⚠️ No hay entradas detectadas.")
        return

    # 4. Backtesting
    results_df = backtest(entries, df_30m)
    metrics = evaluate_trades(results_df)

    # 5. Logging
    log_backtest_summary(
        strategy_name=strategy_name,
        timeframe=f"{higher_tf}→30m",
        r_target=r_target,
        metrics=metrics,
        notes="test automatizado"
    )


def batch_test():
    estrategias = ["bullish_engulfing", "retest_entry"]
    timeframes = ["1d", "12H"]
    r_targets = [1.5, 2.0, 2.5]

    for strat in estrategias:
        for tf in timeframes:
            for r in r_targets:
                run_test(strat, tf, r)


if __name__ == "__main__":
    batch_test()
