# trading_bot/backtesting/evaluator.py

import pandas as pd

def evaluate_trades(results_df: pd.DataFrame):
    """
    Calcula estadísticas clave del backtest.

    :param results_df: DataFrame con las operaciones simuladas
    :return: Diccionario con métricas
    """
    total = len(results_df)
    wins = results_df[results_df['result'] == 'win']
    losses = results_df[results_df['result'] == 'loss']
    open_trades = results_df[results_df['result'] == 'open']

    winrate = len(wins) / total * 100 if total > 0 else 0
    avg_r = results_df['r_multiple'].mean()
    max_r = results_df['r_multiple'].max()
    min_r = results_df['r_multiple'].min()

    # Cálculo aproximado de equity curve y drawdown
    equity = results_df['r_multiple'].cumsum()
    peak = equity.cummax()
    drawdown = (equity - peak)
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

# 🧪 Ejemplo de prueba (seguro)
if __name__ == "__main__":
    from logs.logger import log_backtest_summary

    try:
        df = pd.read_csv("logs/backtest_results.csv")
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
        print(f"❌ Error ejecutando prueba desde evaluator.py: {e}")
