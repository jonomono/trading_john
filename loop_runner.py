# trading_bot/loop_runner.py

import time
import traceback
import subprocess
import webbrowser
from realtime.live_scanner import scan_and_trade
from live_trading.exit_manager import gestionar_salidas
from live_trading.position_manager import gestionar_posiciones
from analytics.performance_summarizer import resumir_performance
from live_trading.signal_executor import system_is_healthy
from config import INTERVAL_MINUTES, TREND_TIMEFRAME, SIGNAL_TIMEFRAME


def launch_dashboard():
    try:
        subprocess.Popen(
            ["streamlit", "run", "dashboard/app.py"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        webbrowser.open_new_tab("http://localhost:8501")
        print("📊 Dashboard lanzado en navegador → http://localhost:8501")
    except Exception as e:
        print(f"⚠️ No se pudo lanzar el dashboard: {e}")


def loop_bot():
    print("🔁 Iniciando bot en modo autónomo (escaneo múltiple de estrategias)")
    print(f"🕒 Intervalo de ejecución: cada {INTERVAL_MINUTES} minutos")
    print(f"📊 Timeframes: estructura={TREND_TIMEFRAME}, entrada={SIGNAL_TIMEFRAME}")

    launch_dashboard()

    while True:
        try:
            print(f"\n⏱️ {time.strftime('%Y-%m-%d %H:%M:%S')} → Ejecutando ciclo...")

            # 1. Evaluar posibles salidas por SL o TP
            print("🚪 Evaluando salidas...")
            gestionar_salidas()

            # 2. Escanear oportunidades de entrada
            print("🔍 Escaneando oportunidades...")
            scan_and_trade()

            # 3. Gestionar posiciones abiertas
            print("🧮 Gestionando posiciones abiertas...")
            gestionar_posiciones()

            # 4. Actualizar resumen de performance
            print("📈 Actualizando resumen de rendimiento...")
            resumen = resumir_performance()

            if resumen is not None:
                print(f"📈 Último resumen → Winrate: {resumen['winrate_%']:.1f}%, "
                      f"Avg R: {resumen['avg_r']:.2f}, "
                      f"Ganadoras: {resumen['total_ganadoras']}, "
                      f"Perdedoras: {resumen['total_perdedoras']}")
            else:
                print("📉 No hay suficientes datos para calcular el resumen.")

            # 5. Evaluar salud del sistema
            print("🩺 Evaluando salud del sistema...")
            if system_is_healthy():
                print("✅ Sistema saludable. Continuando operaciones.")
            else:
                print("⛔ Sistema NO saludable. Pausar decisiones de entrada.")

        except Exception as e:
            print(f"\n❌ Error durante el ciclo: {e}")
            traceback.print_exc()

        print(f"\n⏳ Esperando {INTERVAL_MINUTES} minutos para el próximo ciclo...\n")
        time.sleep(INTERVAL_MINUTES * 60)


if __name__ == "__main__":
    loop_bot()
