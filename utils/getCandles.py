# utils/getCandles.py  (fragmento adaptado)
#python -m utils.getCandles adausdt 15m 3000 Ejemplo de uso
import os
import sys
import time
import requests
import pandas as pd
import pytz
from datetime import datetime
from config import TIMEZONE

tz_local = pytz.timezone(TIMEZONE)
API_URL = "https://fapi.binance.com/fapi/v1/klines"
MAX_LIMIT = 1000  # Binance no acepta más de 1000 por petición

def obtener_klines_pandas(symbol: str, interval: str,
                          total: int = 1000, 
                          pause_ms: int = 500) -> pd.DataFrame:
    """
    Descarga hasta 'total' velas de Binance en bloques de MAX_LIMIT (1000),
    concatenándolas en un DataFrame de pandas con zona horaria local.

    Parámetros:
        symbol  (str):         Símbolo Binance (ej. "BTCUSDT").
        interval(str):         Intervalo de vela (ej. "15m", "1h").
        total   (int):         Número total de velas que quieres (puede ser > 1000).
        pause_ms(int):         Milisegundos a esperar entre llamadas (evita rate limits).

    Retorna:
        pd.DataFrame con columnas ["Datetime","Open","High","Low","Close","Volume"].
        Si no hay datos o hay error, devuelve DataFrame vacío.
    """
    all_dfs = []
    fetched = 0
    end_time = None  # timestamp en ms; si es None, Binance usa el "now"

    while fetched < total:
        limit = min(MAX_LIMIT, total - fetched)
        params = {
            "symbol": symbol.upper(),
            "interval": interval,
            "limit": limit
        }
        if end_time is not None:
            # para pedir velas anteriores a 'end_time'
            params["endTime"] = end_time

        try:
            resp = requests.get(API_URL, params=params, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            if not data or (isinstance(data, dict) and data.get("code")):
                print(f"⚠️ Error en respuesta de Binance: {data}")
                break
        except Exception as e:
            print(f"❌ Error al conectar con Binance: {e}")
            break

        # Convertir la estructura cruda a DataFrame
        columnas = [
            "timestamp", "Open", "High", "Low", "Close", "Volume",
            "Close_time", "Quote_asset_volume", "Number_of_trades",
            "Taker_buy_base", "Taker_buy_quote", "Ignore"
        ]
        df = pd.DataFrame(data, columns=columnas)
        if df.empty:
            break

        # Conversión de tipos numéricos
        for col in ["Open", "High", "Low", "Close", "Volume",
                    "Quote_asset_volume", "Taker_buy_base", "Taker_buy_quote"]:
            df[col] = pd.to_numeric(df[col], errors="coerce")
        df["Number_of_trades"] = df["Number_of_trades"].astype(int, errors="ignore")

        # Timestamp a datetime con zona local
        df["timestamp"] = (
            pd.to_datetime(df["timestamp"], unit="ms", utc=True)
              .dt.tz_convert(tz_local)
        )
        df = df.rename(columns={"timestamp": "Datetime"})
        df = df[["Datetime", "Open", "High", "Low", "Close", "Volume"]]
        df = df.astype({
            "Open": "float64",
            "High": "float64",
            "Low": "float64",
            "Close": "float64",
            "Volume": "float64"
        })

        # Agregamos este bloque a la lista
        all_dfs.append(df)
        fetched += len(df)

        # Calculamos el próximo end_time: la vela más antigua que obtuvimos, menos 1ms
        oldest_ts = df["Datetime"].min()
        # Convertimos esa fecha a milisegundos UTC
        ts_ms = int(oldest_ts.tz_convert("UTC").timestamp() * 1000)
        end_time = ts_ms - 1

        # Pausa para no golpear la API demasiado rápido
        time.sleep(pause_ms / 1000.0)

        # Si Binance devolvió menos de 'limit', significa que ya no hay más velas
        if len(df) < limit:
            break

    if not all_dfs:
        return pd.DataFrame()  # no se obtuvo nada

    # Concatenamos todos los DataFrames, ordenamos por fecha descendente y
    # si pedimos N velas, devolvemos solo las N más recientes
    resultado = pd.concat(all_dfs, ignore_index=True)
    resultado = resultado.sort_values(by="Datetime", ascending=False)
    return resultado.head(total).reset_index(drop=True)

def guardar_klines_csv(symbol: str, interval: str, total: int = 1000):
    """
    Descarga 'total' velas y las guarda en data/SYMBOL_interval.csv.
    """
    df = obtener_klines_pandas(symbol, interval, total)
    if df.empty:
        print(f"⚠️ No se obtuvieron datos para {symbol} en intervalo {interval}.")
        return

    os.makedirs("data", exist_ok=True)
    archivo = f"data/{symbol.upper()}_{interval}.csv"
    df.to_csv(archivo, index=False)
    print(f"✅ Archivo guardado en: {archivo}")

# Bloque principal solo para uso directo por terminal:
if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Uso: python utils/getCandles.py SYMBOL INTERVAL [TOTAL]")
        print("Ejemplo: python utils/getCandles.py BTCUSDT 15m 2000")
        sys.exit(1)

    símbolo = sys.argv[1]
    intervalo = sys.argv[2]
    total_entradas = int(sys.argv[3]) if len(sys.argv) > 3 else 1000
    guardar_klines_csv(símbolo, intervalo, total_entradas)
