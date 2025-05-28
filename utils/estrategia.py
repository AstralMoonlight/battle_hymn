# utils/estrategia.py
import os
from pygame import mixer
from config import SYMBOL  # si deseas usarlo en los prints

# Inicializa el reproductor una vez
mixer.init()

diferencia_di = 1

# Rutas de sonido
SONIDO_LONG = os.path.join("wav", "sound2.wav")
SONIDO_SHORT = os.path.join("wav", "sound3.wav")

def reproducir_sonido(ruta):
    try:
        if os.path.exists(ruta):
            mixer.music.load(ruta)
            mixer.music.play()
        else:
            print(f"⚠️ Archivo de sonido no encontrado: {ruta}")
    except Exception as e:
        print(f"⚠️ Error al reproducir sonido: {e}")

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
        reproducir_sonido(SONIDO_LONG)

    elif short_cond:
        extra = " (✅ Mejorado por precio > centro Bollinger)" if close > bb_centro else ""
        print(f"🔴 Señal SHORT recomendada{extra}")
        reproducir_sonido(SONIDO_SHORT)
    else:
        print("⚪ Sin señal clara, esperar confirmación.")
