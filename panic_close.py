# panic_close.py

import pandas as pd
from datetime import datetime
import os
import sys
import io
from realtime.binance_feed import get_ohlcv
from analytics.performance_summarizer import resumir_performance  # NUEVO: importa la función resumen

# Forzar salida en UTF-8 (evita errores con emojis en consola Windows)
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

OPEN_POSITIONS_PATH = "live_trading/open_positions.csv"
TRADE_LOG_PATH = "live_trading/trade_log.csv"

def load_open_positions():
    if not os.path.exists(OPEN_POSITIONS_PATH):
        print("[ERROR] No se encontró el archivo de posiciones abiertas.")
        return pd.DataFrame()
    try:
        df = pd.read_csv(OPEN_POSITIONS_PATH, parse_dates=["datetime"])
        return df
    except Exception as e:
        print(f"[ERROR] Error al cargar open_positions.csv: {e}")
        return pd.DataFrame()

def get_last_price(symbol):
    try:
        df = get_ohlcv(symbol.replace("USDT", "/USDT"), "1m", limit=1)
        if not df.empty:
            return df["close"].iloc[-1]
    except Exception as e:
        print(f"[ERROR] Error obteniendo precio para {symbol}: {e}")
    return None

def append_to_trade_log(df):
    if df.empty:
        print("[INFO] No hay posiciones que cerrar.")
        return

    logs = []
    for _, row in df.iterrows():
        exit_price = get_last_price(row["symbol"])
        if exit_price is None:
            print(f"[ADVERTENCIA] Precio no disponible para {row['symbol']}, se omite.")
            continue

        row["exit_price"] = exit_price
        row["pnl_%"] = ((exit_price - row["entry_price"]) / row["entry_price"]) * 100
        row["pnl_usdt"] = row["pnl_%"] / 100 * row["entry_price"] * row["qty"]
        row["exit_time"] = datetime.utcnow()
        logs.append(row)

    if not logs:
        print("[ADVERTENCIA] No se pudieron cerrar posiciones por falta de precios.")
        return

    df_log = pd.DataFrame(logs)

    if not os.path.exists(TRADE_LOG_PATH):
        df_log.to_csv(TRADE_LOG_PATH, index=False)
    else:
        try:
            existing = pd.read_csv(TRADE_LOG_PATH)
            pd.concat([existing, df_log], ignore_index=True).to_csv(TRADE_LOG_PATH, index=False)
        except Exception as e:
            print(f"[ERROR] Error al escribir en el trade_log: {e}")
            return

    print(f"[OK] {len(df_log)} posiciones cerradas y registradas en trade_log.csv")

def clear_open_positions():
    open_df = load_open_positions()
    if open_df.empty:
        return
    append_to_trade_log(open_df)
    open_df.iloc[0:0].to_csv(OPEN_POSITIONS_PATH, index=False)
    print("[OK] open_positions.csv limpiado correctamente.")
    resumir_performance()  # NUEVO: actualiza el resumen tras cerrar

if __name__ == "__main__":
    print("[INICIO] Ejecutando cierre masivo de posiciones...")
    clear_open_positions()
