# analytics/performance_summarizer.py

import pandas as pd
import os
from datetime import datetime
import pytz

TRADE_LOG_PATH = "live_trading/trade_log.csv"
SUMMARY_PATH = "analytics/performance_summary.csv"

COLUMNS = [
    "datetime", "total_trades", "winrate_%", "avg_r",
    "avg_usdt", "total_ganadoras", "total_perdedoras"
]

def resumir_performance():
    # Crear archivo de resumen vacío si no existe
    if not os.path.exists(SUMMARY_PATH) or os.stat(SUMMARY_PATH).st_size == 0:
        pd.DataFrame(columns=COLUMNS).to_csv(SUMMARY_PATH, index=False)
        print("📄 Archivo performance_summary.csv creado con encabezados.")

    # Verificar existencia del trade log
    if not os.path.exists(TRADE_LOG_PATH) or os.stat(TRADE_LOG_PATH).st_size == 0:
        print("⚠️ No hay operaciones cerradas en el trade log.")
        return

    try:
        df = pd.read_csv(TRADE_LOG_PATH)

        # Forzar datetime y exit_time en UTC
        df["datetime"] = pd.to_datetime(df["datetime"], errors="coerce")
        df["exit_time"] = pd.to_datetime(df["exit_time"], errors="coerce")

        # Localizar ambos campos en UTC si son naive
        df["datetime"] = df["datetime"].apply(lambda x: x.tz_localize("UTC") if pd.notna(x) and x.tzinfo is None else x)
        df["exit_time"] = df["exit_time"].apply(lambda x: x.tz_localize("UTC") if pd.notna(x) and x.tzinfo is None else x)

    except Exception as e:
        print(f"❌ Error leyendo el trade log: {e}")
        return

    # Eliminar registros con fechas inválidas
    mask_invalid = df["datetime"].isna() | df["exit_time"].isna()
    if mask_invalid.any():
        print(f"⚠️ Se eliminaron {mask_invalid.sum()} filas con fechas mal formateadas.")
        print(df.loc[mask_invalid, ["datetime", "exit_time"]])
        df = df[~mask_invalid]

    if df.empty:
        print("⚠️ No hay operaciones válidas para analizar tras filtrar fechas.")
        return

    # Validar columnas necesarias
    required_cols = {"exit_price", "pnl_usdt"}
    if not required_cols.issubset(df.columns):
        print(f"❌ Faltan columnas requeridas: {required_cols - set(df.columns)}")
        return

    df = df.dropna(subset=["exit_price", "pnl_usdt"])
    if df.empty:
        print("⚠️ No hay operaciones con datos suficientes para analizar.")
        return

    # Cálculos de rendimiento
    total_trades = len(df)
    total_ganadoras = (df["pnl_usdt"] > 0).sum()
    total_perdedoras = (df["pnl_usdt"] <= 0).sum()
    winrate = (total_ganadoras / total_trades) * 100

    if "r_multiple" in df.columns:
        avg_r = df["r_multiple"].mean()
    elif "pnl_%" in df.columns:
        min_pnl = df["pnl_%"].min()
        avg_r = df["pnl_%"].mean() / abs(min_pnl) if min_pnl != 0 else 0
    else:
        avg_r = float("nan")

    avg_usdt = df["pnl_usdt"].mean()

    resumen = pd.DataFrame([{
        "datetime": datetime.utcnow().replace(tzinfo=pytz.UTC).strftime("%Y-%m-%d %H:%M:%S"),
        "total_trades": total_trades,
        "winrate_%": round(winrate, 2),
        "avg_r": round(avg_r, 2),
        "avg_usdt": round(avg_usdt, 2),
        "total_ganadoras": total_ganadoras,
        "total_perdedoras": total_perdedoras
    }])

    try:
        resumen.to_csv(SUMMARY_PATH, mode="a", index=False, header=False)
        print("✅ Resumen de performance actualizado.")
        print(resumen.to_string(index=False))
    except Exception as e:
        print(f"❌ Error al guardar el resumen: {e}")

    return resumen.squeeze()

if __name__ == "__main__":
    resumir_performance()
