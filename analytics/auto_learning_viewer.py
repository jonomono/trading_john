# analytics/auto_learning_viewer.py

import streamlit as st
import pandas as pd
from itertools import product
from backtesting.simulator import backtest
from backtesting.evaluator import evaluate_trades
from logs.logger import log_backtest_summary
from config import BINANCE_PAIRS, TIMEFRAMES, STRATEGIES
from strategies.entry_logic import find_entry_signals as bullish_engulfing
from strategies.retest_entry import find_retest_entries as retest_entry

STRATEGY_FUNCTIONS = {
    "bullish_engulfing": bullish_engulfing,
    "retest_entry": retest_entry
}

def mostrar_auto_learning():
    st.title("🧠 Auto-Learning y Evaluación de Estrategias")

    if st.button("🚀 Ejecutar Auto-Learning"):
        resultados = []
        progress = st.progress(0)
        total_tests = len(STRATEGIES) * len(BINANCE_PAIRS) * len(TIMEFRAMES)
        done = 0

        for strategy_name in STRATEGIES:
            func = STRATEGY_FUNCTIONS.get(strategy_name)
            if not func:
                st.warning(f"Estrategia desconocida: {strategy_name}")
                continue

            for symbol, tf in product(BINANCE_PAIRS, TIMEFRAMES):
                try:
                    trades_df = backtest(
                        strategy_func=func,
                        symbol=symbol,
                        timeframe=tf,
                        save_log=False
                    )

                    if trades_df.empty:
                        continue

                    metrics = evaluate_trades(trades_df)

                    log_backtest_summary(
                        strategy_name=strategy_name,
                        symbol=symbol,
                        timeframe=tf,
                        metrics=metrics,
                        notes="Desde Streamlit"
                    )

                    resultados.append({
                        "strategy": strategy_name,
                        "symbol": symbol,
                        "timeframe": tf,
                        **metrics
                    })

                except Exception as e:
                    st.error(f"❌ Error en {strategy_name} | {symbol} | {tf}: {e}")

                done += 1
                progress.progress(done / total_tests)

        st.success("✅ Auto-learning finalizado.")
        
        if resultados:
            df_resultados = pd.DataFrame(resultados)
            df_resultados["score"] = df_resultados["winrate_%"] * df_resultados["avg_r"]
            top5 = df_resultados.sort_values("score", ascending=False).head(5)

            st.subheader("🏆 Top 5 Estrategias Evaluadas")
            st.dataframe(top5)

            csv = top5.to_csv(index=False).encode("utf-8")
            st.download_button("⬇️ Descargar Top 5 CSV", data=csv, file_name="top5_estrategias.csv")
        else:
            st.warning("No se generaron resultados para mostrar.")
