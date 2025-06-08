# realtime/ohlcv_downloader_viewer.py

import os
import glob
import streamlit as st
from config import BINANCE_PAIRS, TIMEFRAMES
from scripts.download_binance import download_ohlcv

def mostrar_descarga_masiva():
    st.title("📥 Descarga de Datos Históricos OHLCV")
    st.markdown("Selecciona qué descargar:")

    descarga_masiva = st.checkbox("📦 Descargar datos para TODOS los pares")
    todos_los_intervalos = st.checkbox("🕒 Incluir TODOS los intervalos de tiempo")
    combinar_en_csv = st.checkbox("🧩 Unir todo en `all_data.csv`", value=True)

    par = st.selectbox("Par de trading", BINANCE_PAIRS) if not descarga_masiva else None
    intervalo = st.selectbox("Intervalo de tiempo", TIMEFRAMES) if not todos_los_intervalos else None
    num_velas = st.slider("Cantidad de velas a descargar", 100, 50000, 5000, step=100)

    if st.button("⬇️ Descargar"):
        try:
            resultados = []
            success_count = 0
            with st.spinner("Descargando datos..."):
                pares = BINANCE_PAIRS if descarga_masiva else [par]
                timeframes = TIMEFRAMES if todos_los_intervalos else [intervalo]

                for simbolo in pares:
                    for tf in timeframes:
                        try:
                            archivo = download_ohlcv(
                                symbol=simbolo,
                                interval=tf,
                                limit=num_velas,
                                append_to_master=combinar_en_csv
                            )

                            if not combinar_en_csv:
                                filename = f"data/{simbolo}_{tf}.csv"
                                if archivo != filename and os.path.exists(archivo):
                                    os.rename(archivo, filename)
                                path = filename
                            else:
                                path = "data/all_data.csv"

                            resultados.append(f"✅ {simbolo}-{tf}: OK → `{path}`")
                            success_count += 1
                        except Exception as e:
                            resultados.append(f"❌ {simbolo}-{tf}: Error → {e}")

                if success_count > 0:
                    msg = "📦 Descarga completada."
                    msg += " Datos agregados a `all_data.csv`." if combinar_en_csv else " Archivos individuales guardados."
                    st.success(f"{msg} Total: {success_count}.")
                else:
                    st.warning("⚠️ No se pudo descargar ningún archivo.")

                with st.expander("🧾 Ver detalles de la descarga"):
                    for r in resultados:
                        st.markdown(r)

                if combinar_en_csv and os.path.exists("data/all_data.csv"):
                    with open("data/all_data.csv", "rb") as f:
                        st.download_button("⬇️ Descargar `all_data.csv`", f, file_name="all_data.csv")

        except Exception as e:
            st.error(f"❌ Error al descargar: {e}")

    st.divider()
    st.subheader("🧨 Eliminar todos los archivos CSV de la carpeta `data/`")
    if st.button("🗑️ Borrar todos los CSV"):
        try:
            csv_files = glob.glob("data/*.csv")
            deleted = 0
            for file in csv_files:
                os.remove(file)
                deleted += 1
            st.success(f"✅ Se eliminaron {deleted} archivos CSV de la carpeta `data/`.")
        except Exception as e:
            st.error(f"❌ Error al eliminar archivos: {e}")
