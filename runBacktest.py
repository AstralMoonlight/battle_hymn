#!/usr/bin/env python3
# runBacktest.py

import sys
import os
from datetime import timedelta

import pandas as pd
import pytz

from config import DIAS_TEST, SALDO_INICIAL, APALANCAMIENTO, TP, SL, CONFIRMACION_AVISO, TIMEZONE
from utils.getCandles import obtener_klines_pandas
from utils.binance_data import cargar_datos_csv
from utils.resample import resamplear
from utils.indicadores import calcular_indicadores
from utils.estrategia import evaluar_senal
from backtest.simulador import simular_operaciones

tz_local = pytz.timezone(TIMEZONE)

_VALID_INTERVALS = {
    "1m", "3m", "5m", "15m", "30m",
    "1h", "2h", "4h", "6h", "8h", "12h",
    "1d", "3d", "1w", "1M"
}


def _interval_to_pandas_offset(interval: str) -> str:
    interval = interval.lower()
    if interval.endswith("m"):
        return f"{interval[:-1]}T"
    if interval.endswith("h"):
        return f"{interval[:-1]}H"
    if interval.endswith("d"):
        return f"{interval[:-1]}D"
    raise ValueError(f"Intervalo no soportado: {interval}")


def _csv_necesita_actualizar(filepath: str, interval: str, total_candles: int) -> bool:
    try:
        df_old = pd.read_csv(
            filepath,
            parse_dates=["Datetime"],
            infer_datetime_format=True
        ).set_index("Datetime")
    except Exception:
        return True

    if len(df_old) < total_candles:
        return True

    last_ts = df_old.index[-1]
    pandas_offset = _interval_to_pandas_offset(interval)
    now_local = pd.Timestamp.now(tz_local)
    floor_ts = now_local.floor(pandas_offset)

    return last_ts < floor_ts


def _asegurar_datos(symbol: str, interval: str, total_candles: int) -> pd.DataFrame:
    if interval not in _VALID_INTERVALS:
        print(f"❌ Intervalo '{interval}' no válido. Usa uno de: {sorted(_VALID_INTERVALS)}")
        return pd.DataFrame()

    carpeta = "data"
    os.makedirs(carpeta, exist_ok=True)
    filename = f"{symbol.upper()}_{interval}.csv"
    filepath = os.path.join(carpeta, filename)

    necesita = True
    if os.path.isfile(filepath):
        if not _csv_necesita_actualizar(filepath, interval, total_candles):
            necesita = False

    if necesita:
        print(f"🌐 Descargando {total_candles} velas de {symbol.upper()} [{interval}] …")
        df_new = obtener_klines_pandas(symbol, interval, total_candles)
        if df_new.empty:
            print(f"❌ No se pudieron descargar velas para {symbol.upper()}-{interval}.")
            return pd.DataFrame()
        df_new = df_new.reset_index().drop_duplicates(subset=["Datetime"], keep="last")
        df_new = df_new.set_index("Datetime")
        if len(df_new) > total_candles:
            df_new = df_new.sort_index(ascending=False).head(total_candles).sort_index()
        df_new.to_csv(filepath, index=True)
        print(f"✅ Archivo actualizado: {filepath}")
        return df_new

    df_old = pd.read_csv(
        filepath,
        parse_dates=["Datetime"],
        infer_datetime_format=True
    ).set_index("Datetime")
    if len(df_old) > total_candles:
        df_old = df_old.sort_index(ascending=False).head(total_candles).sort_index()
    return df_old


def run_backtest(symbol: str, interval: str, total_candles: int) -> dict:
    df = _asegurar_datos(symbol, interval, total_candles)
    if df.empty:
        return {}

    df = df.sort_index(ascending=True)
    df = calcular_indicadores(df)
    df = df.last(f"{DIAS_TEST}D")
    if df.empty:
        print(f"❌ No hay datos en los últimos {DIAS_TEST} días para {symbol.upper()}-{interval}.")
        return {}

    saldo = SALDO_INICIAL
    operacion_activa = False
    tipo_operacion = None
    entrada = 0.0

    longs = shorts = ganadoras = perdedoras = operaciones = 0
    senal_contador = {"long": 0, "short": 0}

    # Variables para TP/SL intrabar
    NivelTP = None
    NivelSL = None

    for i in range(1, len(df)):
        fila = df.iloc[i]
        fecha = df.index[i]
        precio_open = fila["Open"]
        high = fila["High"]
        low = fila["Low"]
        precio_close = fila["Close"]
        fecha_str = fecha.strftime("%Y-%m-%d %H:%M:%S")

        # 1) Si hay operación activa, verificar intrabar TP/SL
        if operacion_activa:
            if tipo_operacion == "long":
                if low <= NivelSL:
                    precio_salida = NivelSL
                    razon = "SL"
                elif high >= NivelTP:
                    precio_salida = NivelTP
                    razon = "TP"
                else:
                    variacion_raw = (precio_close - entrada) / entrada
                    variacion_pct = variacion_raw * 100 * APALANCAMIENTO
                    print(f"🕒 {fecha_str} | LONG activa sin tocar TP/SL | P/L actual: {variacion_pct:.2f}%")
                    continue
            else:  # short
                if high >= NivelSL:
                    precio_salida = NivelSL
                    razon = "SL"
                elif low <= NivelTP:
                    precio_salida = NivelTP
                    razon = "TP"
                else:
                    variacion_raw = (entrada - precio_close) / entrada
                    variacion_pct = variacion_raw * 100 * APALANCAMIENTO
                    print(f"🕒 {fecha_str} | SHORT activa sin tocar TP/SL | P/L actual: {variacion_pct:.2f}%")
                    continue

            variacion_raw = (precio_salida - entrada) / entrada
            if tipo_operacion == "short":
                variacion_raw *= -1
            variacion_pct = variacion_raw * 100 * APALANCAMIENTO
            ganancia = saldo * (variacion_pct / 100)
            saldo += ganancia

            operaciones += 1
            if variacion_pct > 0:
                ganadoras += 1
            else:
                perdedoras += 1
            if tipo_operacion == "long":
                longs += 1
            else:
                shorts += 1

            print(f"✅ CIERRE {tipo_operacion.upper()} por {razon} a {precio_salida:.2f} | {fecha_str} | P/L={variacion_pct:.2f}% | Saldo={saldo:.2f} USDT")

            operacion_activa = False
            tipo_operacion = None
            senal_contador = {"long": 0, "short": 0}
            continue

        # 2) Si NO hay operación activa, evaluar señal en vela anterior
        ventana = df.iloc[:i]
        senal = evaluar_senal(ventana, solo_tipo=True)

        if senal:
            senal_contador[senal] += 1
            faltan = CONFIRMACION_AVISO - senal_contador[senal]

            if senal_contador[senal] >= CONFIRMACION_AVISO:
                entrada = precio_open
                tipo_operacion = senal
                operacion_activa = True
                senal_contador = {"long": 0, "short": 0}

                if tipo_operacion == "long":
                    NivelTP = entrada * (1 + (TP/100) / APALANCAMIENTO)
                    NivelSL = entrada * (1 + (SL/100) / APALANCAMIENTO)
                else:  # short
                    NivelTP = entrada * (1 - (TP/100) / APALANCAMIENTO)
                    NivelSL = entrada * (1 - (SL/100) / APALANCAMIENTO)

                print(f"📈 ENTRADA CONFIRMADA {tipo_operacion.upper()} | {fecha_str} | Open={entrada:.2f} | TP={NivelTP:.2f} | SL={NivelSL:.2f}")
            else:
                print(f"👀 {fecha_str} | Señal {senal.upper()} ({senal_contador[senal]}/{CONFIRMACION_AVISO}) → faltan {faltan}")
                otro = "short" if senal == "long" else "long"
                senal_contador[otro] = 0

    # 3) Resumen final
    rentabilidad = ((saldo / SALDO_INICIAL) - 1) * 100
    print("\n📊 RESULTADOS BACKTEST:\n")
    print(f"🔁 Operaciones ejecutadas: {operaciones}")
    print(f"🟢 Longs: {longs}     🔴 Shorts: {shorts}")
    print(f"✅ Ganadoras: {ganadoras} ❌ Perdedoras: {perdedoras}\n")
    print(f"💰 Saldo inicial: {SALDO_INICIAL:.2f} USDT")
    print(f"💵 Saldo final  : {saldo:.2f} USDT")
    print(f"📈 Rentabilidad : {rentabilidad:.2f}%")

    # Retornar diccionario con métricas
    return {
        "Operaciones": operaciones,
        "Longs": longs,
        "Shorts": shorts,
        "Ganadoras": ganadoras,
        "Perdedoras": perdedoras,
        "Saldo Final": round(saldo, 2),
        "Rentabilidad (%)": round(rentabilidad, 2)
    }


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Uso: python runBacktest.py <SYMBOL> <INTERVAL> <TOTAL_CANDLES>")
        print("Ejemplo: python runBacktest.py BTCUSDT 15m 2000")
        sys.exit(1)

    symbol_arg = sys.argv[1]
    interval_arg = sys.argv[2]
    total_candles_arg = int(sys.argv[3])

    _ = run_backtest(symbol_arg, interval_arg, total_candles_arg)
