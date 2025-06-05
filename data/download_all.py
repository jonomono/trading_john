# trading_bot/data/download_all.py

from download_data import download_data

# Timeframes compatibles con yfinance (traducidos desde nuestros timeframes)
timeframes = {
    "1d": "1d",
    "12h": "60m",  # descargamos 1h y luego agregamos a 12h manualmente
    "8h": "60m",   # idem
    "4h": "60m",   # idem
    "1h": "60m",
    "30m": "30m"
}

# Fechas
start_date = "2023-01-01"
end_date = "2023-12-31"

# Descarga directa de los que yfinance soporta
direct_intervals = ["1d", "60m", "30m"]

# Descargar directamente disponibles
for tf in direct_intervals:
    download_data("BTC-USD", tf, start_date, end_date)
