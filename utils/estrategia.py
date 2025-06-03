# utils/estrategia.py
"""Estrategia DI‑SMA v2
----------------------
Lógica de generación de señales LONG/SHORT basada en:
- Cruce real entre SMA_CORTA y SMA_LARGA (no mera posición).
- Diferencia dinámica entre +DI y ‑DI (percentil 60 de las últimas 100 velas).
- ADX por encima de umbral *y* en pendiente ascendente.
- RSI por encima/por debajo de RSI_CORTE y con pendiente coherente.

Incluye:
- Reproducción opcional de sonidos.
- Posibilidad de retornar sólo el tipo de señal con ``solo_tipo=True``.
- Impresión de mensajes amigables.

Requisitos del ``DataFrame``:
    RSI, +DI, -DI, ADX,
    SMA{SMA_CORTA}, SMA{SMA_LARGA}, Close
Opcional: BB_Media (para comentarios sobre Bollinger).
"""

from __future__ import annotations

import os
from typing import Optional

import pandas as pd
from pygame import mixer

import config

# ────────────────────────────────────────────────────────────────────────────────
# Audio helpers
# ────────────────────────────────────────────────────────────────────────────────

mixer.init()
SONIDO_LONG = os.path.join("wav", "sound2.wav")
SONIDO_SHORT = os.path.join("wav", "sound3.wav")

def _reproducir_sonido(ruta: str) -> None:
    """Reproduce un archivo de sonido si existe y Pygame está operativo."""
    try:
        if os.path.exists(ruta):
            mixer.music.load(ruta)
            mixer.music.play()
        else:
            print(f"⚠️ Archivo de sonido no encontrado: {ruta}")
    except Exception as exc:  # pylint: disable=broad-except
        print(f"⚠️ Error al reproducir sonido: {exc}")

# ────────────────────────────────────────────────────────────────────────────────
# Signal Engine
# ────────────────────────────────────────────────────────────────────────────────

def evaluar_senal(df: pd.DataFrame, solo_tipo: bool = False) -> Optional[str]:
    """Evalúa la última vela del *DataFrame* y determina si hay señal.

    Parámetros
    ----------
    df : pd.DataFrame
        Velas con indicadores calculados.
    solo_tipo : bool, optional
        Si *True*, devuelve «long», «short» o *None* sin imprimir ni reproducir
        sonidos.  Por defecto *False*.
    """
    # ─── Validaciones básicas ────────────────────────────────────────────────
    if df is None or len(df) < 3:
        return None

    # Columnas requeridas
    required_cols = {"RSI", "+DI", "-DI", "ADX", "Close",
                     f"SMA{config.SMA_CORTA}", f"SMA{config.SMA_LARGA}"}
    missing = required_cols.difference(df.columns)
    if missing:
        print(f"⚠️ Falta(n) columna(s) en df: {sorted(missing)}")
        return None

    # ─── Extracción de valores actuales y previos ────────────────────────────
    curr = df.iloc[-1]
    prev = df.iloc[-2]

    rsi, prev_rsi = float(curr["RSI"]), float(prev["RSI"])
    plus_di, minus_di = float(curr["+DI"]), float(curr["-DI"])
    adx, prev_adx = float(curr["ADX"]), float(prev["ADX"])

    sma_fast = float(curr[f"SMA{config.SMA_CORTA}"])
    prev_fast = float(prev[f"SMA{config.SMA_CORTA}"])
    sma_slow = float(curr[f"SMA{config.SMA_LARGA}"])
    prev_slow = float(prev[f"SMA{config.SMA_LARGA}"])

    close_price = float(curr["Close"])
    bb_centro = curr.get("BB_Media")  # Puede no existir

    # ─── Umbral DI dinámico ──────────────────────────────────────────────────
    di_gap_series = (df["+DI"] - df["-DI"]).abs()
    dynamic_di = di_gap_series.tail(100).quantile(0.60)
    diff_threshold = max(config.DIFERENCIA_DI, dynamic_di)

    # ─── Condiciones auxiliares ──────────────────────────────────────────────
    cross_up   = prev_fast <= prev_slow and sma_fast > sma_slow
    cross_down = prev_fast >= prev_slow and sma_fast < sma_slow

    di_gap_long  = plus_di  - minus_di
    di_gap_short = minus_di - plus_di

    adx_ok = adx > config.ADX_THRESHOLD and adx > prev_adx
    rsi_long_ok  = rsi > config.RSI_CORTE and (rsi - prev_rsi) > 0
    rsi_short_ok = rsi < config.RSI_CORTE and (rsi - prev_rsi) < 0

    # ─── Señales LONG / SHORT ────────────────────────────────────────────────
    long_cond = (
        cross_up and
        di_gap_long >= diff_threshold and
        adx_ok and
        rsi_long_ok
    )

    short_cond = (
        cross_down and
        di_gap_short >= diff_threshold and
        adx_ok and
        rsi_short_ok
    )

    # ─── Solo tipo ───────────────────────────────────────────────────────────
    if solo_tipo:
        if long_cond:
            return "long"
        if short_cond:
            return "short"
        return None

    # ─── Mensajes & sonido ───────────────────────────────────────────────────
    if long_cond:
        extra = (" (⛑ Rebote bajo BB_Media)" if bb_centro is not None and
                  close_price < float(bb_centro) else "")
        print(f"🟢 {config.SYMBOL} Señal LONG{extra}")
        _reproducir_sonido(SONIDO_LONG)

    elif short_cond:
        extra = (" (⛑ Rebote sobre BB_Media)" if bb_centro is not None and
                  close_price > float(bb_centro) else "")
        print(f"🔴 {config.SYMBOL} Señal SHORT{extra}")
        _reproducir_sonido(SONIDO_SHORT)

    else:
        print(f"⚪ {config.SYMBOL} Sin señal clara, esperar confirmación.")

    return None
