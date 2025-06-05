# trading_bot/realtime/binance_feed.py
import ccxt
import pandas as pd

# Cliente de Binance
binance = ccxt.binance()

# Carga los mercados una vez para evitar errores de símbolo
try:
    AVAILABLE_MARKETS = binance.load_markets()
except Exception as e:
    print(f"❌ Error cargando mercados de Binance: {e}")
    AVAILABLE_MARKETS = {}

def normalizar_symbol(symbol):
    """
    Convierte 'BTCUSDT' o cualquier símbolo plano en formato 'BASE/QUOTE'
    y verifica si está disponible en Binance.
    """
    if symbol in AVAILABLE_MARKETS:
        return symbol

    if "/" not in symbol and len(symbol) > 4:
        base = symbol[:-4]
        quote = symbol[-4:]
        candidate = f"{base}/{quote}"
        if candidate in AVAILABLE_MARKETS:
            return candidate

    print(f"❌ Símbolo no válido o no disponible en Binance: {symbol}")
    return None

def get_ohlcv(symbol="BTCUSDT", timeframe="30m", limit=100):
    """
    Descarga velas OHLCV desde Binance.
    """
    try:
        symbol_n = normalizar_symbol(symbol)
        if not symbol_n:
            return pd.DataFrame()

        data = binance.fetch_ohlcv(symbol_n, timeframe, limit=limit)
        df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['datetime'] = pd.to_datetime(df['timestamp'], unit='ms')
        return df[['datetime', 'open', 'high', 'low', 'close', 'volume']]
    except Exception as e:
        print(f"❌ Error al obtener OHLCV para {symbol}: {e}")
        return pd.DataFrame()

def get_latest_price(symbol="BTCUSDT"):
    """
    Obtiene el último precio de mercado desde Binance.
    """
    try:
        symbol_n = normalizar_symbol(symbol)
        if not symbol_n:
            return None

        ticker = binance.fetch_ticker(symbol_n)
        if ticker and 'last' in ticker and ticker['last'] is not None:
            return float(ticker['last'])
        else:
            print(f"⚠️ Ticker inválido o sin 'last' para {symbol_n}")
            return None
    except Exception as e:
        print(f"❌ Error obteniendo precio para {symbol}: {e}")
        return None
