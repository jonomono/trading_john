import os
import pandas as pd

# Archivos y cabeceras necesarias
FILES = {
    "live_trading/open_positions.csv": [
        "datetime", "symbol", "entry_price", "sl", "qty", "order_id"
    ],
    "live_trading/trade_log.csv": [
        "datetime", "exit_time", "symbol", "entry_price", "exit_price",
        "sl", "qty", "order_id", "pnl_usdt", "pnl_%", "r_multiple", "reason"
    ],
    "analytics/performance_summary.csv": [
        "datetime", "total_trades", "winrate_%", "avg_r",
        "avg_usdt", "total_ganadoras", "total_perdedoras"
    ],
    "logs/summary_log.csv": [
        "datetime", "total_trades", "winrate_%", "avg_r",
        "avg_usdt", "total_ganadoras", "total_perdedoras"
    ]
}

def reset_csv_files(force_reset=False):
    for path, columns in FILES.items():
        folder = os.path.dirname(path)
        if not os.path.exists(folder):
            os.makedirs(folder)
            print(f"📁 Carpeta creada: {folder}")

        if not os.path.exists(path):
            pd.DataFrame(columns=columns).to_csv(path, index=False)
            print(f"✅ {path} creado con cabeceras.")
            continue

        try:
            df = pd.read_csv(path)

            # Asegurar que están todas las columnas requeridas
            current_cols = list(df.columns)
            missing_cols = [col for col in columns if col not in current_cols]

            if force_reset:
                pd.DataFrame(columns=columns).to_csv(path, index=False)
                print(f"🔄 {path} reiniciado con cabeceras correctas.")
            elif missing_cols:
                for col in missing_cols:
                    df[col] = ""  # Rellenar columnas faltantes con cadena vacía
                df = df[columns]  # Reordenar columnas
                df.to_csv(path, index=False)
                print(f"🛠️ {path} actualizado añadiendo columnas faltantes: {missing_cols}")
            elif current_cols != columns:
                df = df[columns]  # Reordenar columnas si están desordenadas
                df.to_csv(path, index=False)
                print(f"🔃 {path} columnas reordenadas.")
            else:
                print(f"✅ {path} OK.")
        except Exception as e:
            print(f"❌ Error leyendo {path}: {e}")
            if force_reset:
                pd.DataFrame(columns=columns).to_csv(path, index=False)
                print(f"🔄 {path} reiniciado por error de lectura.")

if __name__ == "__main__":
    # Puedes activar o desactivar la sobrescritura total aquí
    reset_csv_files(force_reset=True)
