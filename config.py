# trading_bot/config.py

PAIRS_TO_ANALYZE = [
    "BTC/USDT", "ETH/USDT", "SOL/USDT",
    "DOGE/USDT", "XRP/USDT", "LTC/USDT",
    "AVAX/USDT", "ADA/USDT", "TRX/USDT",
    "DOT/USDT", "PEPE/USDT"
]

STRATEGIES = ["retest_entry", "bullish_engulfing"]  # orden de prioridad
DEFAULT_RISK_PCT = 1.0

# 🕒 Timeframes configurables
TREND_TIMEFRAME = "15m"     # Estructura de mercado
SIGNAL_TIMEFRAME = "1m"     # Entrada

# 🕒 Intervalo de ejecución para bucles (solo usado por loop_autonomo.py)
try:
    INTERVAL_MINUTES
except NameError:
    INTERVAL_MINUTES = 1  # valor por defecto si no está definido

