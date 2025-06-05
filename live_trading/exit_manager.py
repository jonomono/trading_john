# live_trading/exit_manager.py

import pandas as pd
import os
from datetime import datetime
import pytz
from realtime.binance_feed import get_latest_price
from live_trading.logger import log_trade

def gestionar_salidas(open_path="live_trading/open_positions.csv"):
    """
    Evalúa cada posición abierta para decidir si debe cerrarse por SL o pérdida de momentum.
    Registra los cierres con log_trade() y actualiza las posiciones abiertas.
    """
    if not os.path.exists(open_path) or os.stat(open_path).st_size == 0:
        print("📭 No hay posiciones abiertas para evaluar.")
        return

    try:
        df_open = pd.read_csv(open_path)
    except Exception as e:
        print(f"❌ Error al leer {open_path}: {e}")
        return

    # Verificación preventiva de columnas mínimas necesarias
    columnas_requeridas = ["symbol", "entry_price", "sl", "qty", "datetime", "order_id"]
    if not all(col in df_open.columns for col in columnas_requeridas):
        print(f"❌ Columnas faltantes en {open_path}. Se necesitan: {columnas_requeridas}")
        return

    posiciones_a_mantener = []

    for _, row in df_open.iterrows():
        try:
            symbol = row["symbol"]
            entry_price = float(row["entry_price"])
            sl = float(row["sl"])
            qty = float(row["qty"])
            order_id = row.get("order_id", "N/A")

            # 🛠️ Asegurar datetime localizado
            dt_open = pd.to_datetime(row.get("datetime", datetime.utcnow()), errors="coerce")
            if dt_open.tzinfo is None:
                dt_open = dt_open.tz_localize("UTC")
        except Exception as e:
            print(f"❌ Error procesando fila: {e}")
            continue

        precio_actual = get_latest_price(symbol)
        if precio_actual is None:
            print(f"❌ No se pudo obtener precio para {symbol}. Se mantiene posición.")
            posiciones_a_mantener.append(row)
            continue

        # Evaluar condiciones de salida
        if precio_actual <= sl:
            razon_salida = "SL hit"
        elif precio_actual < entry_price * 1.01:
            razon_salida = "Loss of momentum"
        else:
            posiciones_a_mantener.append(row)
            continue

        # Cálculo de PnL
        pnl_usdt = (precio_actual - entry_price) * qty
        pnl_pct = ((precio_actual / entry_price) - 1) * 100
        r_multiple = pnl_pct / abs(((sl / entry_price) - 1) * 100)

        # Registro de cierre
        log_trade({
            "datetime": dt_open.isoformat(),
            "exit_time": datetime.utcnow().replace(tzinfo=pytz.UTC).isoformat(),
            "symbol": symbol,
            "entry_price": entry_price,
            "exit_price": precio_actual,
            "sl": sl,
            "qty": qty,
            "order_id": order_id,
            "pnl_usdt": round(pnl_usdt, 2),
            "pnl_%": round(pnl_pct, 2),
            "r_multiple": round(r_multiple, 2),
            "reason": razon_salida
        })

        print(f"📤 Cerrando posición en {symbol} a {precio_actual:.8f} USDT por: {razon_salida}")

    # Guardar las posiciones aún abiertas
    try:
        df_restante = pd.DataFrame(posiciones_a_mantener)
        df_restante.to_csv(open_path, index=False)
    except Exception as e:
        print(f"❌ Error al guardar {open_path}: {e}")

if __name__ == "__main__":
    gestionar_salidas()
