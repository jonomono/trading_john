import pandas as pd
import os

def load_trade_log(path="live_trading/trade_log.csv"):
    if not os.path.exists(path) or os.stat(path).st_size == 0:
        print("⚠️ El archivo trade_log.csv está vacío o no existe.")
        return pd.DataFrame()

    try:
        df = pd.read_csv(path, parse_dates=["datetime"])
    except pd.errors.EmptyDataError:
        print("⚠️ trade_log.csv existe pero está vacío o malformado.")
        return pd.DataFrame()
    
    return df

def simulate_pnl(df, price_buffer=0.002):
    """
    Añade columna de 'exit_price' simulada y calcula PnL bruto.
    """
    if df.empty:
        print("⚠️ Log vacío.")
        return df

    # Simular salida: asumimos TP con un pequeño buffer (ejemplo: +0.2%)
    df["exit_price"] = df["entry_price"] * (1 + price_buffer)

    # PnL simulado (sin apalancamiento)
    df["pnl_%"] = ((df["exit_price"] - df["entry_price"]) / df["entry_price"]) * 100
    df["pnl_usdt"] = df["pnl_%"] / 100 * df["entry_price"] * df["qty"]

    return df

def show_summary(df):
    if df.empty:
        print("ℹ️ Nada que mostrar.")
        return

    total_trades = len(df)
    total_pnl = df["pnl_usdt"].sum()
    avg_pnl = df["pnl_usdt"].mean()

    print(f"📊 Resumen:")
    print(f"  - Operaciones simuladas: {total_trades}")
    print(f"  - PnL total: {total_pnl:.2f} USDT")
    print(f"  - PnL medio por trade: {avg_pnl:.2f} USDT")

if __name__ == "__main__":
    df = load_trade_log()
    df = simulate_pnl(df)
    show_summary(df)

    if not df.empty:
        pd.set_option('display.max_rows', 50)
        print("\n🧾 Detalle:")
        print(df[["datetime", "symbol", "entry_price", "exit_price", "pnl_%", "pnl_usdt"]])
