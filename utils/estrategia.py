# utils/estrategia.py
diferencia_di = 1
def evaluar_senal(df, solo_tipo=False):
    fila = df.iloc[-1]

    rsi = fila["RSI"]
    plus_di = fila["+DI"]
    minus_di = fila["-DI"]
    adx = fila["ADX"]
    sma9 = fila["SMA9"]
    sma20 = fila["SMA20"]
    close = fila["Close"]
    bb_centro = fila["BB_Media"]

    long_cond = (
        rsi > 50 and
        plus_di > minus_di and
        (plus_di - minus_di) >= diferencia_di and
        adx > 22 and
        sma9 > sma20
    )

    short_cond = (
        rsi < 50 and
        minus_di > plus_di and
        (minus_di - plus_di) >= diferencia_di and
        adx > 22 and
        sma9 < sma20
    )

    if solo_tipo:
        if long_cond:
            return "long"
        elif short_cond:
            return "short"
        else:
            return None

    if long_cond:
        extra = " (✅ Mejorado por precio < centro Bollinger)" if close < bb_centro else ""
        print(f"🟢 Señal LONG recomendada{extra}")
    elif short_cond:
        extra = " (✅ Mejorado por precio > centro Bollinger)" if close > bb_centro else ""
        print(f"🔴 Señal SHORT recomendada{extra}")
    else:
        print("⚪ Sin señal clara, esperar confirmación.")
