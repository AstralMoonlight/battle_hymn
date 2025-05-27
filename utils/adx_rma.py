# utils/adx_rma.py
import pandas as pd

def calcular_adx_rma(df, window=14):
    high = df['High']
    low = df['Low']
    close = df['Close']

    df['TR'] = pd.concat([
        high - low,
        (high - close.shift()).abs(),
        (low - close.shift()).abs()
    ], axis=1).max(axis=1)

    df['+DM'] = (high - high.shift()).where((high - high.shift()) > (low.shift() - low), 0.0).clip(lower=0)
    df['-DM'] = (low.shift() - low).where((low.shift() - low) > (high - high.shift()), 0.0).clip(lower=0)

    def rma(series, length):
        return series.ewm(alpha=1/length, adjust=False).mean()

    tr_rma = rma(df['TR'], window)
    plus_dm_rma = rma(df['+DM'], window)
    minus_dm_rma = rma(df['-DM'], window)

    df['+DI'] = 100 * plus_dm_rma / tr_rma
    df['-DI'] = 100 * minus_dm_rma / tr_rma
    df['DX'] = 100 * (df['+DI'] - df['-DI']).abs() / (df['+DI'] + df['-DI'])
    df['ADX'] = rma(df['DX'], window)

    df.drop(columns=['TR', '+DM', '-DM', 'DX'], inplace=True)
    return df
