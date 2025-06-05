# live_trading/position_manager.py

import pandas as pd
import os
from datetime import datetime
from realtime.binance_feed import get_ohlcv

OPEN_POSITIONS_PATH = "live_trading/open_positions.csv"
TRADE_LOG_PATH = "live_trading/trade_log.csv"

def load_open_positions():
    """
    Carga las posiciones abiertas desde el archivo CSV.
    """
    if not os.path.exists(OPEN_POSITIONS_PATH) or os.stat(OPEN_POSITIONS_PATH).st_size == 0:
        print("ℹ️ No hay posiciones abiertas (archivo no existe o está vacío).")
        return pd.DataFrame()

    try:
        df = pd.read_csv(OPEN_POSITIONS_PATH, parse_dates=["datetime"])
        if df.empty:
            print("ℹ️ El archivo de posiciones abiertas está vacío.")
        return df
    except pd.errors.EmptyDataError:
        print("⚠️ Archivo open_positions.csv está vacío o malformado.")
        return pd.DataFrame()
    except Exception as e:
        print(f"❌ Error cargando open_positions.csv: {e}")
        return pd.DataFrame()

def save_open_positions(df):
    """
    Guarda el DataFrame actualizado en open_positions.csv.
    """
    try:
        df.to_csv(OPEN_POSITIONS_PATH, index=False)
    except Exception as e:
        print(f"❌ Error al guardar open_positions.csv: {e}")

def append_to_trade_log(row, exit_price):
    """
    Añade una operación cerrada al trade_log.csv, incluyendo order_id si está presente.
    """
    try:
        row = row.copy()

        # Asegurar campos clave
        if "datetime" not in row or pd.isna(row["datetime"]):
            row["datetime"] = datetime.utcnow().isoformat()

        row["exit_price"] = exit_price
        row["exit_time"] = datetime.utcnow().isoformat()

        row["pnl_%"] = round(((exit_price - row["entry_price"]) / row["entry_price"]) * 100, 4)
        row["pnl_usdt"] = round((row["pnl_%"] / 100) * row["entry_price"] * row["qty"], 4)

        if row.get("sl") and row["entry_price"] != row["sl"]:
            risk = abs(row["entry_price"] - row["sl"])
            reward = abs(exit_price - row["entry_price"])
            row["r_multiple"] = round(reward / risk, 2)
        else:
            row["r_multiple"] = 0.0

        log_row = pd.DataFrame([row])

        # Forzar que datetime y exit_time sean válidos
        log_row["datetime"] = pd.to_datetime(log_row["datetime"], errors="coerce")
        log_row["exit_time"] = pd.to_datetime(log_row["exit_time"], errors="coerce")

        if not os.path.exists(TRADE_LOG_PATH) or os.stat(TRADE_LOG_PATH).st_size == 0:
            log_row.to_csv(TRADE_LOG_PATH, index=False)
        else:
            df_log = pd.read_csv(TRADE_LOG_PATH)
            pd.concat([df_log, log_row], ignore_index=True).to_csv(TRADE_LOG_PATH, index=False)

        print(f"📒 Log actualizado: {row['symbol']} cerrado a {exit_price}")
    except Exception as e:
        print(f"❌ Error al guardar en el trade log: {e}")

def gestionar_posiciones():
    """
    Evalúa las posiciones abiertas y las cierra si alcanzan SL o TP.
    """
    df = load_open_positions()
    if df.empty:
        return

    posiciones_a_cerrar = []

    for idx, row in df.iterrows():
        symbol = row["symbol"]
        entry = row["entry_price"]
        sl = row["sl"]
        tp = entry * 1.003  # TP fijo (+0.3%)

        try:
            df_price = get_ohlcv(symbol.replace("USDT", "/USDT"), "1m", limit=1)
            if df_price.empty:
                print(f"⚠️ Precio no disponible para {symbol}.")
                continue

            last_price = df_price["close"].iloc[-1]

            if last_price <= sl:
                print(f"🔻 SL alcanzado en {symbol}: {last_price:.6f}")
                append_to_trade_log(row, last_price)
                posiciones_a_cerrar.append(idx)

            elif last_price >= tp:
                print(f"🎯 TP alcanzado en {symbol}: {last_price:.6f}")
                append_to_trade_log(row, last_price)
                posiciones_a_cerrar.append(idx)

        except Exception as e:
            print(f"❌ Error al procesar {symbol}: {e}")

    if posiciones_a_cerrar:
        df.drop(index=posiciones_a_cerrar, inplace=True)
        save_open_positions(df)
        print(f"\n📉 {len(posiciones_a_cerrar)} posición(es) eliminadas de open_positions.csv\n")
    else:
        print("🔒 Ninguna posición alcanzó SL ni TP en este ciclo.")
