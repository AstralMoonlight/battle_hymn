# utils/binance_data.py

import pandas as pd
import os
import requests
import pytz
from config import SYMBOL, BASE_INTERVAL_STR, LIMIT, CSV_FILE, TIMEZONE

tz_local = pytz.timezone(TIMEZONE)

def guardar_datos_si_existen(df, ruta):
    if df.empty:
        print(f"⚠️ No se descargaron datos. Archivo no será guardado: {ruta}")
        return False
    df.to_csv(ruta)
    print(f"✅ Datos guardados correctamente en {ruta}")
    return True

def obtener_klines():
    url = "https://fapi.binance.com/fapi/v1/klines"
    params = {"symbol": SYMBOL, "interval": BASE_INTERVAL_STR, "limit": LIMIT}
    response = requests.get(url, params=params)

    try:
        data = response.json()
        if not data or (isinstance(data, dict) and data.get("code")):
            print(f"⚠️ Error al obtener datos: {data}")
            return pd.DataFrame()
    except Exception as e:
        print(f"❌ Error al parsear JSON: {e}")
        return pd.DataFrame()

    df = pd.DataFrame(data, columns=[
        "timestamp", "Open", "High", "Low", "Close", "Volume",
        "Close_time", "Quote_asset_volume", "Number_of_trades",
        "Taker_buy_base", "Taker_buy_quote", "Ignore"
    ])
    df = df.astype({"Open": float, "High": float, "Low": float, "Close": float, "Volume": float})
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit='ms')
    df["timestamp"] = df["timestamp"].dt.tz_localize("UTC").dt.tz_convert(tz_local)
    df.set_index("timestamp", inplace=True)
    return df

def cargar_datos_locales():
    if os.path.exists(CSV_FILE):
        df = pd.read_csv(CSV_FILE, index_col="timestamp", parse_dates=True)
        df.index = df.index.tz_localize("UTC").tz_convert(tz_local) if df.index.tz is None else df.index.tz_convert(tz_local)
        return df
    return pd.DataFrame()

def guardar_datos_locales(df):
    if df.empty:
        print(f"⚠️ No se guardó archivo porque el DataFrame está vacío: {CSV_FILE}")
        return
    os.makedirs(os.path.dirname(CSV_FILE), exist_ok=True)
    df.to_csv(CSV_FILE)

def actualizar_datos():
    df_local = cargar_datos_locales()
    df_nuevo = obtener_klines()

    if df_nuevo.empty:
        print("⚠️ No se recibieron datos nuevos desde Binance.")
        return df_local

    if df_local.empty:
        df = df_nuevo
    else:
        ultimo = df_local.index[-1]
        df_nuevo = df_nuevo[df_nuevo.index > ultimo]
        if df_nuevo.empty:
            #print("ℹ️ No hay nuevas velas para agregar.")
            return df_local
        df = pd.concat([df_local, df_nuevo])

    guardar_datos_locales(df)
    return df


def obtener_vela_en_formacion():
    import time

    url = "https://fapi.binance.com/fapi/v1/klines"
    params = {"symbol": SYMBOL, "interval": BASE_INTERVAL_STR, "limit": 2}

    max_reintentos = 5
    for intento in range(max_reintentos):
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            if not data or (isinstance(data, dict) and data.get("code")):
                print(f"⚠️ Error al obtener datos en tiempo real: {data}")
                return None

            vela_actual = data[-1]
            columnas = [
                "timestamp", "Open", "High", "Low", "Close", "Volume",
                "Close_time", "Quote_asset_volume", "Number_of_trades",
                "Taker_buy_base", "Taker_buy_quote", "Ignore"
            ]
            df = pd.DataFrame([vela_actual], columns=columnas)
            df = df.astype({"Open": float, "High": float, "Low": float, "Close": float, "Volume": float})
            df["timestamp"] = pd.to_datetime(df["timestamp"], unit='ms')
            df["timestamp"] = df["timestamp"].dt.tz_localize("UTC").dt.tz_convert(tz_local)
            df.set_index("timestamp", inplace=True)
            return df.iloc[0]

        except requests.exceptions.RequestException as e:
            print(f"❌ Error de conexión: {e}")
            print(f"🔁 Reintentando ({intento+1}/{max_reintentos}) en 10 segundos...")
            time.sleep(10)

    print("🛑 No fue posible obtener la vela tras varios intentos.")
    return None

def set_symbol(new_symbol):
    global SYMBOL, CSV_FILE
    SYMBOL = new_symbol.upper()
    CSV_FILE = f"data/{SYMBOL}_{BASE_INTERVAL_STR}.csv"
