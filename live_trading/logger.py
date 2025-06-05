# live_trading/logger.py

import csv
import os
from datetime import datetime, timezone

# Formato ISO 8601 UTC
def utc_now_str():
    return datetime.now(timezone.utc).isoformat()

def log_trade(data, filename="live_trading/trade_log.csv"):
    """
    Guarda una fila de datos de operación en trade_log.csv de forma segura.
    Crea el archivo con encabezado si no existe.
    """

    now_str = utc_now_str()

    # Forzar consistencia de datetime y exit_time
    if not isinstance(data.get("datetime"), str):
        if isinstance(data.get("datetime"), datetime):
            data["datetime"] = data["datetime"].astimezone(timezone.utc).isoformat()
        else:
            data["datetime"] = now_str

    if not isinstance(data.get("exit_time"), str):
        if isinstance(data.get("exit_time"), datetime):
            data["exit_time"] = data["exit_time"].astimezone(timezone.utc).isoformat()
        else:
            data["exit_time"] = now_str

    # Ordenar columnas si es posible
    standard_order = [
        "datetime", "exit_time", "symbol", "entry_price", "exit_price",
        "sl", "qty", "order_id", "pnl_usdt", "pnl_%", "r_multiple", "reason"
    ]
    header = [col for col in standard_order if col in data] + [k for k in data if k not in standard_order]

    file_exists = os.path.isfile(filename)

    try:
        with open(filename, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=header)
            if not file_exists or os.stat(filename).st_size == 0:
                writer.writeheader()
            writer.writerow(data)
        print(f"📒 Operación registrada en {filename}")
    except PermissionError:
        print(f"❌ Error: No se puede acceder a {filename}. ¿Está abierto en Excel u otro programa?")
    except Exception as e:
        print(f"❌ Error inesperado al guardar en {filename}: {e}")


def log_open_position(symbol, entry_price, sl, qty, order_id, filename="live_trading/open_positions.csv"):
    """
    Registra una nueva posición abierta en open_positions.csv.
    """
    now = utc_now_str()
    new_row = {
        "datetime": now,
        "symbol": symbol,
        "entry_price": entry_price,
        "sl": sl,
        "qty": qty,
        "order_id": order_id
    }

    file_exists = os.path.isfile(filename)

    try:
        with open(filename, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=list(new_row.keys()))
            if not file_exists or os.stat(filename).st_size == 0:
                writer.writeheader()
            writer.writerow(new_row)
        print(f"✅ Posición registrada en {filename}")
    except PermissionError:
        print(f"❌ Error: No se puede acceder a {filename}. ¿Está abierto en Excel u otro programa?")
    except Exception as e:
        print(f"❌ Error inesperado al guardar en {filename}: {e}")
