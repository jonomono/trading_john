# trading_bot/main_realtime.py

import subprocess
import webbrowser
from realtime.live_scanner import scan_and_trade
from live_trading.position_manager import gestionar_posiciones
from live_trading.exit_manager import gestionar_salidas
from analytics.performance_summarizer import resumir_performance
from live_trading.signal_executor import system_is_healthy


def launch_dashboard():
    """Lanza el panel de Streamlit en segundo plano."""
    try:
        subprocess.Popen(["streamlit", "run", "dashboard/app.py"],
                         stdout=subprocess.DEVNULL,
                         stderr=subprocess.DEVNULL)
        webbrowser.open_new_tab("http://localhost:8501")
        print("📊 Dashboard lanzado en navegador → http://localhost:8501")
    except Exception as e:
        print(f"⚠️ No se pudo lanzar el dashboard: {e}")


if __name__ == "__main__":
    launch_dashboard()

    print("\n🔍 Iniciando escaneo puntual del mercado...\n")
    scan_and_trade()

    print("\n📉 Evaluando posiciones abiertas...\n")
    gestionar_posiciones()

    print("\n🔚 Evaluando posibles cierres de posiciones...\n")
    gestionar_salidas()

    print("\n📊 Generando resumen de performance...\n")
    resumen = resumir_performance()

    if resumen is not None:
        print(f"📈 Último resumen → Winrate: {resumen['winrate_%']:.1f}%, "
              f"Avg R: {resumen['avg_r']:.2f}, "
              f"Ganadoras: {resumen['total_ganadoras']}, "
              f"Perdedoras: {resumen['total_perdedoras']}")
    else:
        print("📉 No hay suficientes datos para calcular el resumen.")

    print("\n🧪 Evaluando salud del sistema...\n")
    if system_is_healthy():
        print("✅ El sistema está saludable. Listo para operar.")
    else:
        print("⛔ El sistema NO está saludable. Se recomienda pausar operaciones.")
