# trading_bot/live_trading/risk_manager.py

def calcular_qty_por_riesgo(capital_usdt, riesgo_pct, precio_entrada, precio_stop):
    """
    Calcula la cantidad a comprar en base al riesgo definido.

    Parámetros:
    - capital_usdt (float): capital total disponible en USDT.
    - riesgo_pct (float): porcentaje del capital a arriesgar en la operación (ej. 1.5).
    - precio_entrada (float): precio de entrada de la operación.
    - precio_stop (float): precio de stop-loss de la operación.

    Retorna:
    - float: cantidad de tokens a comprar.
    """
    if any(v <= 0 for v in [capital_usdt, riesgo_pct, precio_entrada, precio_stop]):
        print("[ERROR] Parámetros inválidos para calcular el tamaño de posición.")
        return 0.0

    riesgo_total = capital_usdt * (riesgo_pct / 100)
    distancia_stop = abs(precio_entrada - precio_stop)

    if distancia_stop == 0:
        print("[ERROR] El stop-loss no puede ser igual al precio de entrada.")
        return 0.0

    qty = riesgo_total / distancia_stop
    return round(qty, 6)  # Ajustar decimales si es necesario según el activo

