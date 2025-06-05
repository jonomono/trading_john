# realtime/live_scanner.py

import random
from config import PAIRS_TO_ANALYZE, STRATEGIES, TREND_TIMEFRAME, SIGNAL_TIMEFRAME
from realtime.binance_feed import get_ohlcv
from strategies.structure_analysis import detect_structure, classify_trend
from strategies.entry_logic import find_entry_signals
from strategies.retest_entry import find_retest_entries
from live_trading.signal_executor import execute_signal
from live_trading.logger import log_open_position  # ✅ Corrección de ruta real

def scan_and_trade():
    for symbol in PAIRS_TO_ANALYZE:
        print(f"\n🔍 Escaneando {symbol}")
        print(f"🕒 Timeframes: estructura={TREND_TIMEFRAME}, entrada={SIGNAL_TIMEFRAME}")

        try:
            # 1. Obtener velas actuales
            df_fast = get_ohlcv(symbol, SIGNAL_TIMEFRAME, limit=200)
            df_slow = get_ohlcv(symbol, TREND_TIMEFRAME, limit=200)

            if df_slow.empty or df_fast.empty:
                print(f"⚠️ Sin datos para {symbol}. Saltando.")
                continue

            # 2. Detectar tendencia
            df_slow = detect_structure(df_slow, window=3)
            trend = classify_trend(df_slow)
            print(f"📈 Tendencia detectada: {trend}")

            # 3. Probar estrategias en orden
            signal_found = False
            last_signal = None

            for strategy in STRATEGIES:
                print(f"🔁 Probando estrategia: {strategy}")

                if strategy == "bullish_engulfing":
                    entries = find_entry_signals(df_fast, trend)
                elif strategy == "retest_entry":
                    entries = find_retest_entries(df_fast, trend)
                else:
                    print(f"❌ Estrategia no válida: {strategy}")
                    continue

                if entries:
                    last_signal = entries[-1]
                    print(f"✅ Señal detectada con {strategy} @ {last_signal['entry_price']}, SL: {last_signal['sl']}")
                    signal_found = True
                    break

            # 4. Ejecutar si se encontró señal
            if signal_found and last_signal:
                symbol_clean = symbol.replace("/", "")
                entry_price = last_signal["entry_price"]
                sl = last_signal["sl"]
                qty = last_signal.get("qty", 1)  # Valor por defecto si no está presente
                order_id = random.randint(10000000, 99999999)

                execute_signal(
                    entry_price=entry_price,
                    sl=sl,
                    symbol=symbol_clean
                )

                log_open_position(
                    symbol=symbol_clean,
                    entry_price=entry_price,
                    sl=sl,
                    qty=qty,
                    order_id=order_id
                )
            else:
                print("🚫 Ninguna estrategia generó señal.")

        except Exception as e:
            print(f"❌ Error analizando {symbol}: {e}")
