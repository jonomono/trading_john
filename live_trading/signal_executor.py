# live_trading/signal_executor.py

import pandas as pd
import os
from datetime import datetime, timezone
from live_trading.logger import log_trade, log_open_position  # ✅ Funciones de registro
from live_trading.risk_manager import calcular_qty_por_riesgo  # ✅ Cálculo de tamaño de posición

# Configuración de simulación
OVERRIDE_HEALTH_CHECK = True  # Cambiar a False para activar chequeo real de performance
FAKE_BALANCE_USDT = 1000  # Balance simulado en USDT para pruebas


def system_is_healthy(summary_path="logs/summary_log.csv", threshold_winrate=55, threshold_avg_r=0.5):
    """
    Evalúa si el sistema es saludable para operar en base al resumen de performance.
    """
    if OVERRIDE_HEALTH_CHECK:
        print("⚠️ [OVERRIDE ACTIVADO] Se omite chequeo de salud del sistema.")
        return True

    if not os.path.exists(summary_path) or os.stat(summary_path).st_size == 0:
        print("⚠️ No se encontró el resumen o está vacío.")
        return False

    try:
        df = pd.read_csv(summary_path).tail(10)
    except Exception as e:
        print(f"❌ Error leyendo el log de resumen: {e}")
        return False

    if df.empty or "winrate_%" not in df.columns or "avg_r" not in df.columns:
        print("⚠️ Datos insuficientes para evaluar la salud del sistema.")
        return False

    avg_winrate = df["winrate_%"].mean()
    avg_r = df["avg_r"].mean()

    print(f"🔎 Salud actual del sistema (últimos 10): winrate={avg_winrate:.1f}%, avg_r={avg_r:.2f}")
    return avg_winrate >= threshold_winrate and avg_r >= threshold_avg_r


def simulate_order(entry_price, sl, symbol, qty=1):
    """
    Simula una orden de compra para pruebas sin conexión real.
    """
    print(f"🧪 Simulación de orden ejecutada:")
    print(f"    - Símbolo: {symbol}")
    print(f"    - Entry: {entry_price}")
    print(f"    - SL: {sl}")
    print(f"    - Qty: {qty}")
    print(f"    - ID simulado: {hash((symbol, entry_price, qty)) % 10**8}")
    return {
        "orderId": hash((symbol, entry_price, qty)) % 10**8,
        "status": "FILLED"
    }


def execute_signal(entry_price, sl, symbol="BTCUSDT", risk_pct=1.0):
    """
    Ejecuta una señal de entrada simulada (puede adaptarse a trading real más adelante).
    """
    if not system_is_healthy():
        print("⚠️ Sistema no saludable. No se opera.")
        return

    qty = calcular_qty_por_riesgo(
        capital_usdt=FAKE_BALANCE_USDT,
        riesgo_pct=risk_pct,
        precio_entrada=entry_price,
        precio_stop=sl
    )

    if qty == 0:
        print("⚠️ Tamaño de posición no válido. No se ejecuta la operación.")
        return

    order = simulate_order(entry_price, sl, symbol, qty)

    now = pd.Timestamp.now(tz=timezone.utc)

    # Crear log de operación completo
    log_entry = {
        "datetime": now,
        "exit_time": now,
        "symbol": symbol,
        "entry_price": entry_price,
        "exit_price": entry_price,  # Simulación neutra
        "sl": sl,
        "qty": qty,
        "order_id": order['orderId'],
        "pnl_usdt": 0,
        "pnl_%": 0,
        "r_multiple": 0,
        "reason": "simulated_entry"
    }

    # Registrar operación cerrada (simulada)
    log_trade(log_entry)
    print(f"📒 Orden simulada registrada en log (ID: {order['orderId']})")

   