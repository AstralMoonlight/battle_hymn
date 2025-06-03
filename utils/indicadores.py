# utils/indicadores.py
import pandas as pd
from ta.momentum import RSIIndicator
from ta.volatility import BollingerBands
import config

# ─── Parámetros centralizados ────────────────────────────────────────────────
SMA_FAST  = getattr(config, "SMA_CORTA", 9)      # ej. 9
SMA_SLOW  = getattr(config, "SMA_LARGA", 20)     # ej. 20
SMA_MED   = getattr(config, "SMA_MED", 100)      # opcional, por defecto 100
SMA_LONG  = getattr(config, "SMA_LONG", 200)     # opcional, por defecto 200

RSI_PERIOD = getattr(config, "RSI_PERIOD", 14)
ADX_PERIOD = getattr(config, "ADX_PERIOD", 14)

BB_PERIOD = getattr(config, "BB_PERIOD", 20)
BB_STD    = getattr(config, "BB_STD", 2)

# ─── Helpers ─────────────────────────────────────────────────────────────────
def rma(series: pd.Series, length: int) -> pd.Series:
    """Rolling Moving Average (Wilder)."""
    return series.ewm(alpha=1 / length, adjust=False).mean()

def calcular_adx(df: pd.DataFrame, window: int = ADX_PERIOD) -> pd.DataFrame:
    high, low, close = df['High'], df['Low'], df['Close']

    up_move   = high.diff()
    down_move = -low.diff()

    plus_dm  = up_move.where((up_move > down_move) & (up_move > 0), 0.0)
    minus_dm = down_move.where((down_move > up_move) & (down_move > 0), 0.0)

    tr = pd.concat([
        high - low,
        (high - close.shift()).abs(),
        (low  - close.shift()).abs()
    ], axis=1).max(axis=1)

    tr_rma      = rma(tr,        window)
    plus_dm_rma = rma(plus_dm,   window)
    minus_dm_rma= rma(minus_dm,  window)

    plus_di  = 100 * plus_dm_rma  / tr_rma
    minus_di = 100 * minus_dm_rma / tr_rma
    dx       = 100 * (plus_di - minus_di).abs() / (plus_di + minus_di)
    adx      = rma(dx, window)

    df["+DI"]  = plus_di
    df["-DI"]  = minus_di
    df["ADX"]  = adx
    return df

# ─── Indicadores principales ───────────────────────────────────────────────—
def calcular_indicadores(df: pd.DataFrame) -> pd.DataFrame:
    # SMAs
    df[f"SMA{SMA_FAST}"]  = df["Close"].rolling(window=SMA_FAST).mean()
    df[f"SMA{SMA_SLOW}"]  = df["Close"].rolling(window=SMA_SLOW).mean()
    df[f"SMA{SMA_MED}"]   = df["Close"].rolling(window=SMA_MED).mean()
    df[f"SMA{SMA_LONG}"]  = df["Close"].rolling(window=SMA_LONG).mean()

    # Bollinger Bands
    bb = BollingerBands(close=df["Close"], window=BB_PERIOD, window_dev=BB_STD)
    df["BB_Media"]    = bb.bollinger_mavg()
    df["BB_Superior"] = bb.bollinger_hband()
    df["BB_Inferior"] = bb.bollinger_lband()

    # RSI
    df["RSI"] = RSIIndicator(close=df["Close"], window=RSI_PERIOD).rsi()

    # ADX / DI
    df = calcular_adx(df, window=ADX_PERIOD)
    return df
