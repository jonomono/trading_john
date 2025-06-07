# trading_bot/analytics/summary_viewer.py

import streamlit as st
import pandas as pd
import os

LOG_PATH = "logs/summary_log.csv"

def mostrar_summary_log():
    st.header("📚 Historial de Backtests")

    if not os.path.exists(LOG_PATH):
        st.info("No se encontró el archivo summary_log.csv.")
        return

    df = pd.read_csv(LOG_PATH)

    if df.empty:
        st.warning("⚠️ El archivo está vacío.")
        return

    with st.expander("🔍 Filtro avanzado"):
        estrategia = st.multiselect("Filtrar por estrategia:", options=df["strategy"].unique())
        min_winrate = st.slider("Winrate mínimo (%)", 0, 100, 0)

        if estrategia:
            df = df[df["strategy"].isin(estrategia)]
        df = df[df["winrate_%"] >= min_winrate]

    st.dataframe(df.sort_values("timestamp", ascending=False), use_container_width=True)

    st.subheader("📈 Estadísticas globales")
    col1, col2, col3 = st.columns(3)
    col1.metric("Backtests", len(df))
    col2.metric("Winrate Promedio", f"{df['winrate_%'].mean():.2f}%")
    col3.metric("Avg R Promedio", f"{df['avg_r'].mean():.2f}")

    st.line_chart(df.set_index("timestamp")[["winrate_%"]], use_container_width=True)
