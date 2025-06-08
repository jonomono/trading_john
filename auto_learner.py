# auto_learner.py

import os
from itertools import product
import pandas as pd
from backtesting.simulator import backtest
from backtesting.evaluator import evaluate_trades
from logs.logger import log_backtest_summary
from config import BINANCE_PAIRS, TIMEFRAMES, STRATEGIES

# Importar funciones de estrategia
from strategies.entry_logic import find_entry_signals as bullish_engulfing
from strategies.retest_entry import find_retest_entries as retest_entry

# Mapear nombres a funciones
STRATEGY_FUNCTIONS = {
    "bullish_engulfing": bullish_engulfing,
    "retest_entry": retest_entry
}

def ejecutar_auto_backtest():
    for strategy_name in STRATEGIES:
        strategy_func = STRATEGY_FUNCTIONS.get(strategy_name)
        if not strategy_func:
            print(f"⚠️ Estrategia desconocida: {strategy_name}")
            continue

        for symbol, tf in product(BINANCE_PAIRS, TIMEFRAMES):
            try:
                print(f"⏳ Backtest {strategy_name} | {symbol} | {tf}")
                trades_df = backtest(
                    strategy_func=strategy_func,
                    symbol=symbol,
                    timeframe=tf,
                    save_log=False  # No se guarda aún; lo hacemos tras evaluación
                )

                if trades_df.empty:
                    print(f"⚠️ Sin operaciones: {strategy_name} | {symbol} | {tf}")
                    continue

                # Evaluar métricas
                metrics = evaluate_trades(trades_df)

                # Registrar resumen en el log
                log_backtest_summary(
                    strategy_name=strategy_name,
                    symbol=symbol,
                    timeframe=tf,
                    metrics=metrics,
                    notes="Auto-learning batch"
                )

            except Exception as e:
                print(f"❌ Error en {strategy_name} - {symbol} - {tf}: {e}")

if __name__ == "__main__":
    ejecutar_auto_backtest()
