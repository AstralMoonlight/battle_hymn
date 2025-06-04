# utils/binance_data.py

"""
Módulo: utils/binance_data.py

Este archivo contiene funciones para:
  - Descargar velas (klines) desde la API de Binance Futures.
  - Guardar y actualizar datos localmente en archivos CSV.
  - Cargar datos locales desde CSV.
  - Obtener la vela en formación en tiempo real.
  - Configurar dinámicamente el símbolo de trading y la ruta de CSV asociada.

Requiere las siguientes variables en `config.py`:
  - SYMBOL:            Símbolo de trading por defecto (p. ej. "BTCUSDT").
  - BASE_INTERVAL_STR: Intervalo de tiempo por defecto (p. ej. "15m").
  - LIMIT:             Límite de velas a solicitar por defecto (p. ej. 1000).
  - CSV_FILE:          Ruta de archivo CSV por defecto (p. ej. "data/BTCUSDT_15m.csv").
  - TIMEZONE:          Zona horaria, ej. "America/Santiago".
"""

import os
import time
import requests
import pandas as pd
import pytz
from datetime import datetime

# Importar variables de configuración (sirven como valores por defecto)
from config import SYMBOL, BASE_INTERVAL_STR, LIMIT_API, CSV_FILE, TIMEZONE

# Preparar la zona horaria local
tz_local = pytz.timezone(TIMEZONE)

# URL base de la API de velas de Binance Futures
_API_URL = "https://fapi.binance.com/fapi/v1/klines"


def guardar_datos_si_existen(df: pd.DataFrame, ruta: str) -> bool:
    """
    Guarda el DataFrame como CSV en la ruta indicada si no está vacío.
    Devuelve True si se guardó correctamente, False si el DataFrame estaba vacío.

    Parámetros:
        df   (pd.DataFrame): DataFrame de pandas con datos a guardar.
        ruta (str)         : Ruta completa del archivo CSV destino.

    Retorna:
        bool: True si se escribió el archivo, False si df estaba vacío.
    """
    if df.empty:
        print(f"⚠️ No se guardó archivo porque el DataFrame está vacío: {ruta}")
        return False

    os.makedirs(os.path.dirname(ruta), exist_ok=True)
    df.to_csv(ruta)
    print(f"✅ Datos guardados correctamente en {ruta}")
    return True


def obtener_klines(symbol: str = SYMBOL, interval: str = BASE_INTERVAL_STR, limit: int = LIMIT_API) -> pd.DataFrame:
    """
    Descarga velas (klines) de Binance Futures para el símbolo y intervalo especificados.

    Parámetros:
        symbol   (str): Símbolo de trading (ej. "BTCUSDT").
        interval (str): Intervalo de tiempo (ej. "15m", "1h", "1d").
        limit    (int): Cantidad máxima de velas a solicitar (máximo 1000 por llamada).

    Retorna:
        pd.DataFrame: DataFrame con índice en 'timestamp' (DatetimeIndex con tz local),
                      y columnas: ["Open", "High", "Low", "Close", "Volume",
                                     "Quote_asset_volume", "Number_of_trades",
                                     "Taker_buy_base", "Taker_buy_quote"].
                      Si ocurre un error, devuelve DataFrame vacío.
    """
    params = {"symbol": symbol.upper(), "interval": interval, "limit": limit}

    try:
        response = requests.get(_API_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        # Si Binance devuelve un diccionario con "code" => error
        if not data or (isinstance(data, dict) and data.get("code")):
            print(f"⚠️ Error en respuesta de Binance: {data}")
            return pd.DataFrame()

    except Exception as e:
        print(f"❌ Error al conectar con Binance: {e}")
        return pd.DataFrame()

    # Convertir la lista de listas en DataFrame
    columnas = [
        "timestamp", "Open", "High", "Low", "Close", "Volume",
        "Close_time", "Quote_asset_volume", "Number_of_trades",
        "Taker_buy_base", "Taker_buy_quote", "Ignore"
    ]
    df = pd.DataFrame(data, columns=columnas)

    # Convertir columnas numéricas (vienen como strings)
    for col in ["Open", "High", "Low", "Close", "Volume",
                "Quote_asset_volume", "Taker_buy_base", "Taker_buy_quote"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df["Number_of_trades"] = df["Number_of_trades"].astype(int, errors="ignore")

    # Convertir 'timestamp' (ms desde epoch) a datetime UTC y luego a tz local
    df["timestamp"] = (
        pd.to_datetime(df["timestamp"], unit="ms", utc=True)
          .dt.tz_convert(tz_local)
    )
    # Convertir 'Close_time' a datetime local (opcional, no se usa como índice)
    df["Close_time"] = (
        pd.to_datetime(df["Close_time"], unit="ms", utc=True)
          .dt.tz_convert(tz_local)
    )

    # Indexar por 'timestamp' y seleccionar columnas relevantes
    df.set_index("timestamp", inplace=True)
    df = df[["Open", "High", "Low", "Close", "Volume",
             "Quote_asset_volume", "Number_of_trades",
             "Taker_buy_base", "Taker_buy_quote"]]

    return df


def cargar_datos_locales() -> pd.DataFrame:
    """
    Carga el archivo CSV indicado por CSV_FILE (desde config) y lo devuelve
    como DataFrame indexado por 'timestamp' (DatetimeIndex con tz local).
    Si no existe, devuelve DataFrame vacío.

    Retorna:
        pd.DataFrame: DataFrame con datos locales o vacío si no existe CSV.
    """
    if os.path.exists(CSV_FILE):
        df = pd.read_csv(
            CSV_FILE,
            index_col="timestamp",
            parse_dates=True,
            infer_datetime_format=True
        )
        # Asegurar que el índice tenga la zona horaria local
        if df.index.tz is None:
            df.index = df.index.tz_localize("UTC").tz_convert(tz_local)
        else:
            df.index = df.index.tz_convert(tz_local)
        return df

    return pd.DataFrame()


def guardar_datos_locales(df: pd.DataFrame):
    """
    Guarda el DataFrame en la ruta CSV_FILE indicada en config.py.
    Si df está vacío, no guarda nada.

    Parámetros:
        df (pd.DataFrame): DataFrame a guardar.
    """
    if df.empty:
        print(f"⚠️ No se guardó archivo porque el DataFrame está vacío: {CSV_FILE}")
        return

    os.makedirs(os.path.dirname(CSV_FILE), exist_ok=True)
    df.to_csv(CSV_FILE)
    print(f"✅ Datos locales actualizados en {CSV_FILE}")


def actualizar_datos() -> pd.DataFrame:
    """
    Descarga nuevas velas desde Binance y las concatena con las locales.
    - Si no hay CSV local, descarga 'LIMIT' velas y guarda.
    - Si existe CSV local, agrega únicamente las velas más recientes.

    Retorna:
        pd.DataFrame: DataFrame actualizado (concatenación de antiguos + nuevos).
    """
    df_local = cargar_datos_locales()
    df_nuevo = obtener_klines()

    if df_nuevo.empty:
        print("⚠️ No se recibieron datos nuevos desde Binance.")
        return df_local

    if df_local.empty:
        df = df_nuevo
    else:
        ultimo = df_local.index[-1]
        # Tomar solo velas posteriores al último índice local
        df_nuevo = df_nuevo[df_nuevo.index > ultimo]
        if df_nuevo.empty:
            # No hay velas nuevas
            return df_local
        df = pd.concat([df_local, df_nuevo])

    guardar_datos_locales(df)
    return df


def obtener_vela_en_formacion() -> pd.Series or None: # type: ignore
    """
    Solicita la vela en formación (la última no cerrada completamente).
    Realiza hasta 5 reintentos si hay error de conexión.

    Retorna:
        pd.Series con datos de la vela en formación (índice en 'timestamp' con tz local),
        o None si no fue posible tras varios intentos.
    """
    params = {"symbol": SYMBOL.upper(), "interval": BASE_INTERVAL_STR, "limit": 2}
    max_reintentos = 5

    for intento in range(max_reintentos):
        try:
            response = requests.get(_API_URL, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            # Validar respuesta
            if not data or (isinstance(data, dict) and data.get("code")):
                print(f"⚠️ Error en respuesta de Binance: {data}")
                return None

            # La vela en formación es el último elemento de la lista
            vela_actual = data[-1]
            columnas = [
                "timestamp", "Open", "High", "Low", "Close", "Volume",
                "Close_time", "Quote_asset_volume", "Number_of_trades",
                "Taker_buy_base", "Taker_buy_quote", "Ignore"
            ]
            df = pd.DataFrame([vela_actual], columns=columnas)

            # Convertir tipos numéricos
            for col in ["Open", "High", "Low", "Close", "Volume",
                        "Quote_asset_volume", "Taker_buy_base", "Taker_buy_quote"]:
                df[col] = pd.to_numeric(df[col], errors="coerce")
            df["Number_of_trades"] = df["Number_of_trades"].astype(int, errors="ignore")

            # Convertir 'timestamp' a datetime con tz local
            df["timestamp"] = (
                pd.to_datetime(df["timestamp"], unit="ms", utc=True)
                  .dt.tz_convert(tz_local)
            )
            df.set_index("timestamp", inplace=True)

            # Devolver la Serie de la vela en formación
            return df.iloc[0]

        except requests.exceptions.RequestException as e:
            print(f"❌ Error de conexión: {e}")
            print(f"🔁 Reintentando ({intento+1}/{max_reintentos}) en 10 segundos...")
            time.sleep(10)

    print("🛑 No fue posible obtener la vela tras varios intentos.")
    return None


def set_symbol(new_symbol: str):
    """
    Actualiza las variables SYMBOL y CSV_FILE para que apunten a un nuevo símbolo
    de trading. Útil para cambiar dinámicamente el par sin editar config.py.

    Ejemplo:
        set_symbol("ETHUSDT")
        # Ahora SYMBOL = "ETHUSDT"
        # CSV_FILE  = "data/ETHUSDT_<intervalo>.csv"

    Parámetros:
        new_symbol (str): Nuevo símbolo de trading (p. ej. "ETHUSDT").
    """
    global SYMBOL, CSV_FILE
    SYMBOL = new_symbol.upper()
    # Reconstruir CSV_FILE en base al nuevo SYMBOL y al intervalo por defecto
    CSV_FILE = f"data/{SYMBOL}_{BASE_INTERVAL_STR}.csv"
    print(f"🔄 Símbolo cambiado a {SYMBOL}, CSV_FILE actualizado a '{CSV_FILE}'")


def cargar_datos_csv(symbol: str, interval: str) -> pd.DataFrame:
    """
    Carga el CSV generado por getCandles.py y lo devuelve como DataFrame indexado
    por "Datetime". El archivo debe residir en data/{SYMBOL}_{interval}.csv.
    Lanza FileNotFoundError si no existe.

    Parámetros:
        symbol   (str): Símbolo de trading en Binance (ej. "BTCUSDT").
        interval (str): Intervalo de vela (ej. "15m", "1h", "1d").

    Retorna:
        pd.DataFrame: DataFrame con índice 'Datetime' (DatetimeIndex con tz local),
                      y columnas ["Open", "High", "Low", "Close", "Volume"].
    """
    ruta = f"data/{symbol.upper()}_{interval}.csv"
    if not os.path.isfile(ruta):
        raise FileNotFoundError(f"No existe el archivo: {ruta}")

    # Leer CSV y parsear la columna "Datetime"
    df = pd.read_csv(
        ruta,
        parse_dates=["Datetime"],
        infer_datetime_format=True
    )
    # Asegurar que el índice tenga la zona horaria local
    df.set_index("Datetime", inplace=True)
    if df.index.tz is None:
        df.index = df.index.tz_localize("UTC").tz_convert(tz_local)
    else:
        df.index = df.index.tz_convert(tz_local)

    # Solo conservar columnas relevantes (pueden haber otras en CSV)
    columnas_relevantes = ["Open", "High", "Low", "Close", "Volume"]
    df = df.loc[:, df.columns.intersection(columnas_relevantes)]

    return df
