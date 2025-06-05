# trading_bot/logs/analyzer.py

import pandas as pd
import os
from datetime import datetime

TRADE_LOG_PATH = "live_trading/trade_log.csv"
SUMMARY_PATH = "logs/summary_log.csv"

def calcular_r(row):
    risk = abs(row["entry_price"] - row["sl"])
    if risk == 0:
        return 0
    reward = abs(row["exit_price"] - row["entry_price"])
    return reward / risk

def generar_summary():
    if not os.path.exists(TRADE_LOG_PATH) or os.stat(TRADE_LOG_PATH).st_size == 0:
        print("⚠️ No hay datos en trade_log.csv para analizar.")
        return

    df = pd.read_csv(TRADE_LOG_PATH, parse_dates=["datetime", "exit_time"])
    if df.empty or "exit_price" not in df.columns:
        print("⚠️ El archivo no contiene operaciones cerradas.")
        return

    df["r_multiple"] = df.apply(calcular_r, axis=1)
    df["is_win"] = df["pnl_usdt"] > 0

    summary = {
        "timestamp": datetime.utcnow(),
        "total_trades": len(df),
        "winrate_%": df["is_win"].mean() * 100,
        "avg_r": df["r_multiple"].mean(),
        "max_drawdown": df["pnl_usdt"].cumsum().min(),  # asumiendo capital inicial = 0
        "strategy": "realtime_sim",  # puedes personalizarlo si registras estrategia
        "timeframe": "realtime"
    }

    df_summary = pd.DataFrame([summary])

    if not os.path.exists(SUMMARY_PATH):
        df_summary.to_csv(SUMMARY_PATH, index=False)
    else:
        pd.concat([pd.read_csv(SUMMARY_PATH), df_summary]).to_csv(SUMMARY_PATH, index=False)

    print("✅ Resumen generado y guardado en logs/summary_log.csv")

def analyze_logs(summary_path=SUMMARY_PATH, winrate_threshold=55, avg_r_threshold=0.5):
    try:
        df = pd.read_csv(summary_path)
    except FileNotFoundError:
        print("❌ No se encontró el archivo de log. Ejecuta primero algunas operaciones.")
        return

    print("📊 Análisis del log de operaciones\n")

    print("🔹 Últimas 5 ejecuciones:")
    print(df.tail(5)[['timestamp', 'strategy', 'winrate_%', 'avg_r', 'max_drawdown']])
    print()

    best = df.sort_values(by='avg_r', ascending=False).iloc[0]
    worst = df.sort_values(by='avg_r', ascending=True).iloc[0]

    print("✅ Mejor ejecución:")
    print(best[['timestamp', 'strategy', 'timeframe', 'avg_r', 'winrate_%']])
    print()

    print("❌ Peor ejecución:")
    print(worst[['timestamp', 'strategy', 'timeframe', 'avg_r', 'winrate_%']])
    print()

    last_n = df.tail(10)
    avg_winrate = last_n['winrate_%'].mean()
    avg_r = last_n['avg_r'].mean()

    print(f"🧠 Salud del sistema (últimos 10 runs):")
    print(f"Promedio winrate: {avg_winrate:.2f}%")
    print(f"Promedio R: {avg_r:.2f}")

    if avg_winrate >= winrate_threshold and avg_r >= avg_r_threshold:
        print("✅ Estado del sistema: SANO. Puedes operar.")
    else:
        print("⚠️ Estado del sistema: NO SANO. Ajustar parámetros o estrategias.\n")

    grouped = df.groupby("strategy")[['winrate_%', 'avg_r']].mean().sort_values(by='avg_r', ascending=False)
    print("📈 Rendimiento medio por estrategia:")
    print(grouped.round(2))


# Si se ejecuta directamente
if __name__ == "__main__":
    generar_summary()
    analyze_logs()
