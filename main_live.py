# trading_bot/main_live.py

import os
import pandas as pd
from live_trading.signal_executor import execute_signal
from live_trading.signal_executor import system_is_healthy

SIGNALS_PATH = "logs/backtest_results.csv"
TRADE_LOG_PATH = "live_trading/trade_log.csv"
SYMBOL = "BTCUSDT"

def already_executed(signal_time):
    if not os.path.exists(TRADE_LOG_PATH):
        return False

    trade_log = pd.read_csv(TRADE_LOG_PATH)
    return signal_time in trade_log['datetime'].astype(str).values


def main_live():
    print("\n🤖 Iniciando bot en modo LIVE...")

    if not os.path.exists(SIGNALS_PATH):
        print("❌ No hay señales disponibles.")
        return

    df = pd.read_csv(SIGNALS_PATH)
    df['datetime'] = pd.to_datetime(df['datetime'])

    # Seleccionamos la última señal
    latest_signal = df.iloc[-1]

    # Verificamos si ya se ejecutó
    if already_executed(str(latest_signal['datetime'])):
        print("⏭️ Señal ya ejecutada anteriormente.")
        return

    # Verificamos estado del sistema
    if not system_is_healthy():
        print("⚠️ Sistema no saludable. No se ejecutará la orden.")
        return

    # Ejecutamos la orden
    print(f"🚀 Ejecutando orden de compra en {SYMBOL} @ {latest_signal['entry_price']}")
    execute_signal(
        entry_price=latest_signal['entry_price'],
        sl=latest_signal['sl'],
        symbol=SYMBOL,
        risk_pct=1  # 1% de la cuenta por operación
    )


if __name__ == "__main__":
    main_live()
