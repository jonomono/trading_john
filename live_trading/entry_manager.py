import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from realtime.binance_feed import get_latest_price
from live_trading.logger import log_open_position
import uuid


# Configuración inicial
SYMBOL = "BTCUSDT"
SUPPORT_LEVEL = 65000  # Puedes cargar este valor desde análisis dinámico
SL_PCT = 0.02          # 2% bajo el precio de entrada
QTY = 0.001            # Tamaño de posición fijo (por ahora)

def evaluar_entrada():
    """
    Evalúa si se debe abrir una posición según una condición de entrada simple.
    """
    price = get_latest_price(SYMBOL)

    if price is None:
        print("⚠️ No se pudo obtener el precio actual.")
        return

    # 🔍 Condición de entrada ficticia (ejemplo simple)
    if price <= SUPPORT_LEVEL * 1.01:  # Entrada si el precio está cerca del soporte
        entry_price = price
        sl = entry_price * (1 - SL_PCT)
        order_id = str(uuid.uuid4())  # ID único para la operación

        print(f"📈 Entrada detectada en {entry_price:.2f} | SL: {sl:.2f}")

        # Registrar posición abierta
        log_open_position(
            symbol=SYMBOL,
            entry_price=entry_price,
            sl=sl,
            qty=QTY,
            order_id=order_id,
            side="long"
        )

    else:
        print("⏸️ No se cumplen condiciones de entrada.")

if __name__ == "__main__":
    evaluar_entrada()
