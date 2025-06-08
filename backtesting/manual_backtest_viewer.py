# backtesting/manual_backtest_viewer.py

import streamlit as st
import pandas as pd
from config import BINANCE_PAIRS, TIMEFRAMES
from strategies.structure_analysis import detect_structure, classify_trend
from strategies.entry_logic import find_entry_signals as engulfing_strategy
from strategies.retest_entry import find_retest_entries as retest_strategy
from backtesting.simulator import backtest
from backtesting.evaluator import evaluate_trades
from logs.logger import log_backtest_summary

def mostrar_backtest_manual():
    st.title("🧪 Backtest Manual Personalizado")

    # Selección de parámetros
    par = st.selectbox("Par", BINANCE_PAIRS)
    tf_mayor = st.selectbox("Timeframe de estructura", TIMEFRAMES)
    tf_entrada = st.selectbox("Timeframe de entrada", TIMEFRAMES)
    estrategia = st.selectbox("Estrategia", ["bullish_engulfing", "retest_entry"])
    r_target = st.slider("🎯 R objetivo (Take Profit)", 0.5, 5.0, 2.0, 0.1)

    if st.button("▶️ Ejecutar Backtest"):
        try:
            tf_mayor_file = f"data/{par}_{tf_mayor}.csv"
            tf_entry_file = f"data/{par}_{tf_entrada}.csv"

            df_higher = pd.read_csv(tf_mayor_file)
            df_entry = pd.read_csv(tf_entry_file)

            df_higher['datetime'] = pd.to_datetime(df_higher['datetime'])
            df_entry['datetime'] = pd.to_datetime(df_entry['datetime'])

            df_higher = detect_structure(df_higher, window=5)
            trend = classify_trend(df_higher)
            st.markdown(f"📈 Tendencia detectada en {tf_mayor}: `{trend}`")

            # Entradas
            if estrategia == "bullish_engulfing":
                entries = engulfing_strategy(df_entry, trend)
            elif estrategia == "retest_entry":
                entries = retest_strategy(df_entry, trend)
            else:
                st.error("❌ Estrategia no reconocida.")
                return

            if not entries:
                st.warning("⚠️ No se encontraron entradas para esta configuración.")
                return

            # Backtest
            result_df = backtest(entries, df_entry)

            # Evaluación
            metrics = evaluate_trades(result_df)

            # Guardar log
            log_backtest_summary(
                strategy_name=estrategia,
                timeframe=f"{tf_mayor}→{tf_entrada}",
                r_target=r_target,
                metrics=metrics,
                notes=f"{par} lanzado desde Streamlit"
            )

            # Mostrar resultados
            st.success("✅ Backtest completado")
            for k, v in metrics.items():
                st.markdown(f"**{k}**: {v}")

            st.subheader("📉 Curva de R acumulado")
            result_df["cumulative_r"] = result_df["r_multiple"].cumsum()
            st.line_chart(result_df.set_index("datetime")["cumulative_r"])

        except FileNotFoundError:
            st.error("❌ No se encontraron los archivos CSV para el par o timeframe seleccionado.")
        except Exception as e:
            st.error(f"❌ Error durante el backtest:\n{str(e)}")
