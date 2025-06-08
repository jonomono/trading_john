# trading_bot/backtesting/evaluator.py

import pandas as pd
import os
from logs.logger import log_backtest_summary

def evaluate_trades(results_df: pd.DataFrame) -> dict:
    """
    Calcula estadísticas clave del backtest.

    :param results_df: DataFrame con las operaciones simuladas
    :return: Diccionario con métricas
    """
    if results_df.empty:
        return {
            "total_trades": 0,
            "wins": 0,
            "losses": 0,
            "open_trades": 0,
            "winrate_%": 0.0,
            "avg_r": 0.0,
            "max_r": 0.0,
            "min_r": 0.0,
            "max_drawdown": 0.0
        }

    total = len(results_df)
    wins = results_df[results_df['result'] == 'win']
    losses = results_df[results_df['result'] == 'loss']
    open_trades = results_df[results_df['result'] == 'open']

    winrate = len(wins) / total * 100 if total > 0 else 0
    avg_r = results_df['r_multiple'].mean()
    max_r = results_df['r_multiple'].max()
    min_r = results_df['r_multiple'].min()

    # Cálculo de equity curve y drawdown
    equity = results_df['r_multiple'].cumsum()
    peak = equity.cummax()
    drawdown = equity - peak
    max_drawdown = drawdown.min()

    return {
        "total_trades": total,
        "wins": len(wins),
        "losses": len(losses),
        "open_trades": len(open_trades),
        "winrate_%": round(winrate, 2),
        "avg_r": round(avg_r, 2),
        "max_r": round(max_r, 2),
        "min_r": round(min_r, 2),
        "max_drawdown": round(max_drawdown, 2)
    }


# 🧪 Test manual (ejecución local o desde botón Streamlit)
if __name__ == "__main__":
    try:
        path_resultados = "logs/backtest_results.csv"

        if not os.path.exists(path_resultados):
            raise FileNotFoundError("El archivo de resultados no existe.")

        df = pd.read_csv(path_resultados)

        # Verificación de columnas mínimas necesarias
        required_cols = {"result", "r_multiple"}
        if not required_cols.issubset(df.columns):
            raise ValueError(f"Columnas requeridas faltantes en {path_resultados}")

        metrics = evaluate_trades(df)

        log_backtest_summary(
            strategy_name="bullish_engulfing",
            timeframe="1D→30m",
            r_target=2.0,
            metrics=metrics,
            notes="Estrategia simple con tendencia uptrend"
        )

        print("\n📊 Resultados del Backtest:")
        for key, value in metrics.items():
            print(f"{key}: {value}")

    except Exception as e:
        print(f"❌ Error evaluando el backtest: {e}")
