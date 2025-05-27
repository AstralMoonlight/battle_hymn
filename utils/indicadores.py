# utils/indicadores.py

import pandas as pd
from ta.momentum import RSIIndicator
from ta.volatility import BollingerBands

def rma(series, length):
    return series.ewm(alpha=1 / length, adjust=False).mean()

def calcular_adx(df, window=14):
    high = df['High']
    low = df['Low']
    close = df['Close']

    up_move = high - high.shift()
    down_move = low.shift() - low

    plus_dm = up_move.where((up_move > down_move) & (up_move > 0), 0.0)
    minus_dm = down_move.where((down_move > up_move) & (down_move > 0), 0.0)

    tr_components = pd.concat([
        high - low,
        (high - close.shift()).abs(),
        (low - close.shift()).abs()
    ], axis=1)
    tr = tr_components.max(axis=1)

    tr_rma = rma(tr, window)
    plus_dm_rma = rma(plus_dm, window)
    minus_dm_rma = rma(minus_dm, window)

    plus_di = 100 * plus_dm_rma / tr_rma
    minus_di = 100 * minus_dm_rma / tr_rma
    dx = 100 * (plus_di - minus_di).abs() / (plus_di + minus_di)
    adx = rma(dx, window)

    df["+DI"] = plus_di
    df["-DI"] = minus_di
    df["ADX"] = adx

    return df

def calcular_indicadores(df):
    df["SMA9"] = df["Close"].rolling(window=9).mean()
    df["SMA20"] = df["Close"].rolling(window=20).mean()
    df["SMA100"] = df["Close"].rolling(window=100).mean()
    df["SMA200"] = df["Close"].rolling(window=200).mean()

    bb = BollingerBands(close=df["Close"], window=20, window_dev=2)
    df["BB_Media"] = bb.bollinger_mavg()
    df["BB_Superior"] = bb.bollinger_hband()
    df["BB_Inferior"] = bb.bollinger_lband()

    rsi = RSIIndicator(close=df["Close"], window=14)
    df["RSI"] = rsi.rsi()

    df = calcular_adx(df, window=14)

    return df
