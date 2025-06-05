import time
import traceback
import subprocess
import sys

from realtime.live_scanner import scan_and_trade
from live_trading.exit_manager import gestionar_salidas
from live_trading.position_manager import gestionar_posiciones
from analytics.performance_summarizer import resumir_performance
from live_trading.signal_executor import system_is_healthy
from config import INTERVAL_MINUTES


def lanzar_dashboard():
    """Lanza el panel de Streamlit en segundo plano."""
    try:
        subprocess.Popen(
            [sys.executable, "-m", "streamlit", "run", "dashboard/app.py"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        print("📊 Dashboard lanzado en segundo plano → http://localhost:8501")
    except Exception as e:
        print(f"⚠️ Error al lanzar el dashboard: {e}")


def loop_autonomo():
    print("\n🔁 Iniciando loop autónomo (escaneo + salidas + gestión + performance + salud)")
    print(f"🕒 Intervalo de ejecución: cada {INTERVAL_MINUTES} minutos")

    while True:
        try:
            print(f"\n⏱️ {time.strftime('%Y-%m-%d %H:%M:%S')} → Ejecutando ciclo completo...")

            # 1. Escaneo de oportunidades de entrada
            print("\n🔍 Escaneando oportunidades de entrada...")
            scan_and_trade()

            # 2. Gestión de salidas
            print("\n🚪 Evaluando salidas por SL o TP...")
            gestionar_salidas()

            # 3. Gestión de posiciones abiertas (mantenimiento, actualizaciones)
            print("\n📉 Evaluando posiciones abiertas...")
            gestionar_posiciones()

            # 4. Resumen de performance
            print("\n📊 Generando resumen de performance...")
            resumen = resumir_performance()

            if resumen is not None:
                print(f"📈 Último resumen → Winrate: {resumen['winrate_%']:.1f}%, "
                      f"Avg R: {resumen['avg_r']:.2f}, "
                      f"Ganadoras: {resumen['total_ganadoras']}, "
                      f"Perdedoras: {resumen['total_perdedoras']}")
            else:
                print("📉 No hay suficientes datos para calcular el resumen.")

            # 5. Estado del sistema
            print("\n🧪 Evaluando salud del sistema...")
            if system_is_healthy():
                print("✅ Sistema saludable. Listo para operar.")
            else:
                print("⛔ Sistema NO saludable. Mejor pausar decisiones operativas.")

        except Exception as e:
            print(f"\n❌ Error durante el ciclo: {e}")
            traceback.print_exc()

        print(f"\n⏳ Esperando {INTERVAL_MINUTES} minutos para el próximo ciclo...\n")
        time.sleep(INTERVAL_MINUTES * 60)


if __name__ == "__main__":
    lanzar_dashboard()
    loop_autonomo()
