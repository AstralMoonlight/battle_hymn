# utils/estrategia.py

import os
from pygame import mixer
import config

# Inicializa el reproductor una vez
mixer.init()

# Rutas de sonido
SONIDO_LONG = os.path.join("wav", "sound2.wav")
SONIDO_SHORT = os.path.join("wav", "sound3.wav")


def reproducir_sonido(ruta):
    """
    Reproduce un archivo de sonido si existe. 
    """
    try:
        if os.path.exists(ruta):
            mixer.music.load(ruta)
            mixer.music.play()
        else:
            print(f"⚠️ Archivo de sonido no encontrado: {ruta}")
    except Exception as e:
        print(f"⚠️ Error al reproducir sonido: {e}")


def evaluar_senal(df, solo_tipo=False):
    if df.empty:
        return None

    try:
        fila = df.iloc[-1]
        rsi = fila["RSI"]
        plus_di = fila["+DI"]
        minus_di = fila["-DI"]
        adx = fila["ADX"]
        # Ahora usamos config.SMA_CORTA y config.SMA_LARGA dinámicos
        sma_fast = fila[f"SMA{config.SMA_CORTA}"]
        sma_slow = fila[f"SMA{config.SMA_LARGA}"]
        close = fila["Close"]
        bb_centro = fila["BB_Media"]
    except KeyError as e:
        print(f"⚠️ Falta columna en df: {e}.")
        return None

    # Y aquí referimos a config.RSI_CORTE, config.ADX_THRESHOLD, config.DIFERENCIA_DI…
    long_cond = (
        (rsi > config.RSI_CORTE) and
        (plus_di > minus_di) and
        ((plus_di - minus_di) >= config.DIFERENCIA_DI) and
        (adx > config.ADX_THRESHOLD) and
        (sma_fast > sma_slow)
    )
    short_cond = (
        (rsi < config.RSI_CORTE) and
        (minus_di > plus_di) and
        ((minus_di - plus_di) >= config.DIFERENCIA_DI) and
        (adx > config.ADX_THRESHOLD) and
        (sma_fast < sma_slow)
    )

    if solo_tipo:
        if long_cond:
            return "long"
        elif short_cond:
            return "short"
        else:
            return None

    # Si no es solo_tipo, imprimimos y tocamos sonido:
    if long_cond:
        extra = ""
        if close < bb_centro:
            extra = " (✅ Mejorado por precio < centro Bollinger)"
        print(f"🟢 {config.SYMBOL} Señal LONG recomendada{extra}")
        reproducir_sonido(SONIDO_LONG)

    elif short_cond:
        extra = ""
        if close > bb_centro:
            extra = " (✅ Mejorado por precio > centro Bollinger)"
        print(f"🔴 {config.SYMBOL} Señal SHORT recomendada{extra}")
        reproducir_sonido(SONIDO_SHORT)

    else:
        print(f"⚪ {config.SYMBOL} Sin señal clara, esperar confirmación.")
    """
    Detección de señal con parámetros tomados de config.py:
      - RSI_CORTE: valor de RSI por encima → LONG; por debajo → SHORT.
      - DIFERENCIA_DI: diferencia mínima entre +DI y -DI para considerar fuerza.
      - ADX_THRESHOLD: valor mínimo de ADX para validar tendencia.
      - SMA_CORTA vs SMA_LARGA: cruces de medias para confirmar dirección.

    df debe contener al menos las columnas: ["RSI", "+DI", "-DI", "ADX", 
    f"SMA{SMA_CORTA}", f"SMA{SMA_LARGA}", "Close", "BB_Media"].

    Parámetros:
        df         (pd.DataFrame): Ventana histórica de velas con columnas de indicadores.
        solo_tipo   (bool)        : Si True, retorna solo "long"/"short"/None.
                                   Si False, imprime el mensaje y reproduce sonido.

    Retorna:
        str|None: "long", "short" o None.
    """
    # Asegurarse de que haya al menos 1 fila
    if df.empty:
        return None

    # Tomar la última fila de indicadores
    try:
        fila = df.iloc[-1]
        rsi = fila["RSI"]
        plus_di = fila["+DI"]
        minus_di = fila["-DI"]
        adx = fila["ADX"]
        sma_fast = fila[f"SMA{SMA_CORTA}"]
        sma_slow = fila[f"SMA{SMA_LARGA}"]
        close = fila["Close"]
        bb_centro = fila["BB_Media"]
    except KeyError as e:
        print(f"⚠️ Falta columna en df: {e}. Asegúrate de calcular todos los indicadores.")
        return None

    # Condición LONG
    long_cond = (
        (rsi > RSI_CORTE) and
        (plus_di > minus_di) and
        ((plus_di - minus_di) >= DIFERENCIA_DI) and
        (adx > ADX_THRESHOLD) and
        (sma_fast > sma_slow)
    )

    # Condición SHORT
    short_cond = (
        (rsi < RSI_CORTE) and
        (minus_di > plus_di) and
        ((minus_di - plus_di) >= DIFERENCIA_DI) and
        (adx > ADX_THRESHOLD) and
        (sma_fast < sma_slow)
    )

    if solo_tipo:
        if long_cond:
            return "long"
        elif short_cond:
            return "short"
        else:
            return None

    # Si no es solo_tipo, imprimimos y reproducimos sonido
    if long_cond:
        extra = ""
        if close < bb_centro:
            extra = " (✅ Mejorado por precio < centro Bollinger)"
        print(f"🟢 {SYMBOL} Señal LONG recomendada{extra}")
        reproducir_sonido(SONIDO_LONG)

    elif short_cond:
        extra = ""
        if close > bb_centro:
            extra = " (✅ Mejorado por precio > centro Bollinger)"
        print(f"🔴 {SYMBOL} Señal SHORT recomendada{extra}")
        reproducir_sonido(SONIDO_SHORT)

    else:
        print(f"⚪ {SYMBOL} Sin señal clara, esperar confirmación.")
