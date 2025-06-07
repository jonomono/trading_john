import pandas as pd
import os
from datetime import datetime

def log_backtest_summary(
    strategy_name: str,
    timeframe: str,
    r_target: float,
    metrics: dict,
    notes: str = ""
):
    """
    Guarda un resumen del backtest en un log acumulativo CSV.
    """
    summary_file = "logs/summary_log.csv"
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if not isinstance(metrics, dict):
        print("❌ Error: las métricas no están en formato diccionario.")
        return

    log_entry = {
        "timestamp": now,
        "strategy": strategy_name,
        "timeframe": timeframe,
        "r_target": r_target,
        "total_trades": metrics.get("total_trades", 0),
        "winrate_%": metrics.get("winrate_%", 0),
        "avg_r": metrics.get("avg_r", 0),
        "max_r": metrics.get("max_r", 0),
        "min_r": metrics.get("min_r", 0),
        "max_drawdown": metrics.get("max_drawdown", 0),
        "notes": notes
    }

    if not os.path.exists(summary_file):
        df_log = pd.DataFrame([log_entry])
    else:
        df_log = pd.read_csv(summary_file)
        df_log = pd.concat([df_log, pd.DataFrame([log_entry])], ignore_index=True)

    # Asegurar orden de columnas
    column_order = list(log_entry.keys())
    df_log = df_log[column_order]

    try:
        df_log.to_csv(summary_file, index=False)
        print(f"📚 Log actualizado en {summary_file}")
    except PermissionError:
        print(f"❌ No se puede escribir en {summary_file}. ¿Está abierto en Excel?")
    except Exception as e:
        print(f"❌ Error inesperado al guardar log: {e}")
