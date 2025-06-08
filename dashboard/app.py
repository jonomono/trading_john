import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta, timezone
from realtime.binance_feed import get_ohlcv
from analytics.summary_viewer import mostrar_summary_log
from analytics.auto_learning_viewer import mostrar_auto_learning
from backtesting.simulator import backtest
from backtesting.evaluator import evaluate_trades
from logs.logger import log_backtest_summary
from strategies.structure_analysis import detect_structure, classify_trend
from strategies.entry_logic import find_entry_signals as engulfing_strategy
from strategies.retest_entry import find_retest_entries as retest_strategy
from config import BINANCE_PAIRS, TIMEFRAMES
from realtime.ohlcv_downloader_viewer import mostrar_descarga_masiva
from backtesting.manual_backtest_viewer import mostrar_backtest_manual



# Configuración inicial de Streamlit (debe ir antes que cualquier otro comando)
st.set_page_config(page_title="Panel de Trading", layout="wide")

# Menú lateral de navegación
seccion = st.sidebar.selectbox("📂 Secciones", [
    "📊 Trading en Vivo",
    "📚 Historial de Backtests",
    "🧪 Ejecutar Backtest Manual",
    "📥 Descargar OHLCV",
    "🧹 Reiniciar Datos",
    "📉 Auto-Learning y Evaluador"
])

if seccion == "📊 Trading en Vivo":
    st.title("📊 Panel de Trading Autónomo")

    # Rutas de archivos
    OPEN_PATH = "live_trading/open_positions.csv"
    TRADE_LOG_PATH = "live_trading/trade_log.csv"
    SUMMARY_PATH = "analytics/performance_summary.csv"

    # 🟡 Sección de posiciones abiertas
    st.header("🟡 Posiciones Abiertas")
    try:
        if os.path.exists(OPEN_PATH):
            expected_cols = ["datetime", "symbol", "entry_price", "sl", "qty", "order_id"]

            # Cargar todas las líneas del archivo
            with open(OPEN_PATH, "r", encoding="utf-8") as f:
                lines = f.readlines()

            valid_lines = [lines[0]]  # mantener el encabezado
            for line in lines[1:]:
                if line.count(",") == 5:  # 6 columnas = 5 comas
                    valid_lines.append(line)

            # Si hubo líneas inválidas, sobrescribimos el archivo sin ellas
            if len(valid_lines) != len(lines):
                with open(OPEN_PATH, "w", encoding="utf-8") as f:
                    f.writelines(valid_lines)
                st.warning("⚠️ Se eliminaron algunas líneas corruptas del archivo de posiciones abiertas.")

            df_open = pd.read_csv(OPEN_PATH)

            if list(df_open.columns) != expected_cols:
                st.warning("⚠️ Las columnas del archivo no coinciden con las esperadas.")
                st.write("Columnas actuales:", df_open.columns.tolist())
            elif df_open.empty:
                st.info("No hay posiciones abiertas actualmente.")
            else:
                st.dataframe(df_open)

                # Resumen de posiciones abiertas
                st.subheader("📌 Resumen de Posiciones Abiertas")
                num_open = len(df_open)
                valor_usdt = (df_open["entry_price"] * df_open["qty"]).sum()
                total_tokens = df_open["qty"].sum()
                col1, col2, col3 = st.columns(3)
                col1.metric("📄 Total Posiciones", num_open)
                col2.metric("💵 Valor Total (USDT)", f"{valor_usdt:.2f}")
                col3.metric("📦 Tokens totales", f"{total_tokens:.4f}")
        else:
            st.info("El archivo de posiciones abiertas no existe aún.")
    except pd.errors.EmptyDataError:
        st.warning("⚠️ El archivo de posiciones abiertas está vacío o malformado.")
    except Exception as e:
        st.error(f"❌ Error al cargar las posiciones abiertas:\n{str(e)}")


    # 📘 Sección de historial de operaciones cerradas
    st.header("📘 Historial de Operaciones Cerradas")
    if os.path.exists(TRADE_LOG_PATH) and os.stat(TRADE_LOG_PATH).st_size > 0:
        try:
            df_log = pd.read_csv(TRADE_LOG_PATH)
            df_log["exit_time"] = pd.to_datetime(df_log["exit_time"], utc=True, errors="coerce")
            df_log = df_log.dropna(subset=["exit_time"])

            if df_log.empty:
                st.info("No hay operaciones válidas para mostrar.")
            else:
                st.dataframe(df_log.sort_values("exit_time", ascending=False).head(20))

                # 🔍 Rendimiento por rango
                st.subheader("📆 Rendimiento por Periodo")
                now = datetime.now(timezone.utc)
                ranges = {
                    "🕐 Hoy": df_log[df_log["exit_time"].dt.date == now.date()],
                    "📆 Últimos 7 días": df_log[df_log["exit_time"] >= now - timedelta(days=7)],
                    "📅 Últimos 30 días": df_log[df_log["exit_time"] >= now - timedelta(days=30)],
                    "📊 Histórico": df_log
                }

                for label, df_ in ranges.items():
                    if not df_.empty:
                        trades = len(df_)
                        winrate = (df_["pnl_usdt"] > 0).mean() * 100
                        avg_r = df_.get("r_multiple", pd.Series()).mean() if "r_multiple" in df_.columns else float("nan")
                        avg_pnl = df_["pnl_usdt"].mean()
                        st.markdown(f"**{label}** — Operaciones: {trades}, Winrate: {winrate:.1f}%, Avg R: {avg_r:.2f}, Avg PnL: {avg_pnl:.2f} USDT")
                    else:
                        st.markdown(f"**{label}** — Sin datos disponibles.")

                # 📉 Gráfico de evolución del PnL acumulado
                st.subheader("📈 Evolución del PnL Acumulado")
                df_log = df_log.sort_values("exit_time")
                df_log["cumulative_pnl"] = df_log["pnl_usdt"].cumsum()
                st.line_chart(df_log.set_index("exit_time")["cumulative_pnl"], use_container_width=True)
        except pd.errors.EmptyDataError:
            st.warning("⚠️ El archivo de operaciones cerradas está vacío o malformado.")
        except Exception as e:
            st.error(f"❌ Error al cargar el historial de operaciones:\n{str(e)}")
    else:
        st.info("No hay operaciones cerradas aún.")

    # 📈 Sección de resumen de rendimiento
    st.header("📈 Rendimiento Global")
    if os.path.exists(SUMMARY_PATH) and os.stat(SUMMARY_PATH).st_size > 0:
        try:
            df_summary = pd.read_csv(SUMMARY_PATH, parse_dates=["datetime"])
            if df_summary.empty:
                st.info("El archivo de resumen existe, pero aún no contiene datos.")
            else:
                resumen = df_summary.tail(1).squeeze()
                col1, col2, col3 = st.columns(3)
                col1.metric("✔️ Winrate", f"{resumen['winrate_%']:.1f}%")
                col2.metric("📈 Avg R", f"{resumen['avg_r']:.2f}")
                col3.metric("📊 Total Trades", int(resumen.get("total_ganadoras", 0) + resumen.get("total_perdedoras", 0)))

                # Resumen de capital
                st.subheader("💰 Resumen de Capital")
                if os.path.exists(TRADE_LOG_PATH):
                    df = pd.read_csv(TRADE_LOG_PATH)
                    if "pnl_usdt" in df.columns and not df["pnl_usdt"].empty:
                        pnl_total = df["pnl_usdt"].sum()
                        capital_inicial = 1000.0
                        capital_actual = capital_inicial + pnl_total
                        pnl_pct = (pnl_total / capital_inicial) * 100
                        col1, col2, col3, col4 = st.columns(4)
                        col1.metric("💼 Capital Inicial (€)", f"{capital_inicial:.2f}")
                        col2.metric("🏦 Capital Actual (€)", f"{capital_actual:.2f}")
                        col3.metric("📈 PnL (€)", f"{pnl_total:.2f}")
                        col4.metric("📊 PnL (%)", f"{pnl_pct:.2f}%")

                # 📉 Gráficos históricos de evolución
                st.subheader("📉 Evolución Histórica del Rendimiento")
                df_summary = df_summary.sort_values("datetime")
                df_summary["total_trades"] = df_summary["total_ganadoras"] + df_summary["total_perdedoras"]

                st.line_chart(df_summary.set_index("datetime")[["winrate_%"]], use_container_width=True)
                st.line_chart(df_summary.set_index("datetime")[["avg_r"]], use_container_width=True)
                st.line_chart(df_summary.set_index("datetime")[["total_trades"]], use_container_width=True)
        except pd.errors.EmptyDataError:
            st.warning("⚠️ El archivo performance_summary.csv está vacío o malformado.")
        except Exception as e:
            st.error(f"❌ Error al cargar el resumen de performance:\n{str(e)}")
    else:
        st.warning("📉 No se ha generado aún el resumen de performance.")

    # 🚨 Botón del Pánico para cierre masivo de posiciones
    st.header("🚨 Botón del Pánico")
    st.warning("Esta acción cerrará todas las posiciones abiertas inmediatamente.")
    if st.button("❌ Cerrar TODAS las posiciones"):
        try:
            from panic_close import clear_open_positions
            clear_open_positions()
            st.success("✅ Todas las posiciones fueron cerradas con éxito.")
        except Exception as e:
            st.error(f"❌ Error al ejecutar el cierre masivo:\n{str(e)}")

elif seccion == "📚 Historial de Backtests":
    mostrar_summary_log()

elif seccion == "🧪 Ejecutar Backtest Manual":
    mostrar_backtest_manual()


elif seccion == "📥 Descargar OHLCV":
    mostrar_descarga_masiva()



elif seccion == "🧹 Reiniciar Datos":
    st.title("🧹 Reiniciar Archivos CSV")
    st.warning("⚠️ Esta acción eliminará todos los datos actuales y reiniciará los archivos CSV a su estado inicial.")

    confirmar = st.checkbox("✅ Estoy seguro de que quiero reiniciar todo", value=False)

    if st.button("⚠️ Reiniciar todos los CSV"):
        if confirmar:
            try:
                from utils.reset_csv import reset_csv_files
                reset_csv_files(force_reset=True)
                st.success("✅ Todos los archivos fueron reiniciados correctamente.")
            except Exception as e:
                st.error(f"❌ Error al reiniciar los archivos: {e}")
        else:
            st.info("☝️ Debes confirmar que estás seguro antes de continuar.")

elif seccion == "📉 Auto-Learning y Evaluador":
    mostrar_auto_learning()
