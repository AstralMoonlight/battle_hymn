# utils/consola.py
from config import SYMBOL, ANALYSIS_INTERVAL

def mostrar_ultimo(df):
    if df.empty:
        print("⚠️ DataFrame vacío. No hay datos para mostrar.")
        return

    ultima = df.iloc[-1]
    print(f"\n📍 {ultima.name} — {SYMBOL} ({ANALYSIS_INTERVAL})")
    print(f"RSI        : {ultima['RSI']:.2f}")
    print(f"+DI / -DI  : {ultima['+DI']:.2f} / {ultima['-DI']:.2f}")
    print(f"ADX        : {ultima['ADX']:.2f}")
    print(f"SMA9/20    : {ultima['SMA9']:.2f} / {ultima['SMA20']:.2f}")
    print(f"SMA100/200 : {ultima['SMA100']:.2f} / {ultima['SMA200']:.2f}")
    print(f"Bollinger  : {ultima['BB_Inferior']:.2f} < {ultima['Close']:.2f} < {ultima['BB_Superior']:.2f}")
    print(f"Volumen    : {ultima['Volume']:.2f}")
