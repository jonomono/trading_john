# trading_bot/main.py

import sys
import os
import time
import pandas as pd

# Añadir la raíz del proyecto al path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

# Live trading
from live_trading.entry_manager import evaluar_entrada
from live_trading.exit_manager import gestionar_salidas

# Backtesting
from strategies.structure_analysis import detect_structure, classify_trend
from strategies.entry_logic import find_entry_signals as engulfing_strategy
from strategies.retest_entry import find_retest_entries as retest_strategy
from backtesting.simulator import backtest
from backtesting.evaluator import evaluate_trades
from logs.logger import log_backtest_summary

def run_live_trading(interval_minutes=5):
    print("🚀 Iniciando agente en modo REAL (simulado)")
    while True:
        print("🔍 Evaluando entrada...")
        evaluar_entrada()
        print("📤 Evaluando salidas...")
        gestionar_salidas()
        print(f"⏳ Esperando {interval_minutes} minutos...\n")
        time.sleep(interval_minutes * 60)

def run_backtest(strategy_name="bullish_engulfing", r_target=2.0):
    print(f"\n🧪 Ejecutando backtest con estrategia: {strategy_name}")

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

def main(modo="live", strategy_name="retest_entry", r_target=2.0):
    if modo == "live":
        run_live_trading()
    elif modo == "backtest":
        run_backtest(strategy_name=strategy_name, r_target=r_target)
    else:
        print("❌ Modo no reconocido. Usa 'live' o 'backtest'.")

if __name__ == "__main__":
    # Cambia 'live' por 'backtest' según lo que quieras probar
    main(modo="live", strategy_name="retest_entry", r_target=2.0)
