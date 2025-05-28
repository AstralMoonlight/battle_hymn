# utils/binance_fetcher.py

import time
import pandas as pd
import requests
from datetime import datetime, timedelta
from config import SYMBOL, BASE_INTERVAL_STR, CSV_FILE, TIMEZONE
import pytz

tz_local = pytz.timezone(TIMEZONE)


def get_binance_klines(symbol, interval, start_time, end_time=None, limit=1000):
    url = "https://api.binance.com/api/v3/klines"
    params = {
        "symbol": symbol,
        "interval": interval,
        "limit": limit,
        "startTime": int(start_time.timestamp() * 1000),
    }
    if end_time:
        params["endTime"] = int(end_time.timestamp() * 1000)
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()


def descargar_velas(dias=5, ruta_salida=CSV_FILE):
    ahora = datetime.utcnow()
    inicio = ahora - timedelta(days=dias)
    todas_las_velas = []

    print(f"📥 Descargando velas de {SYMBOL} cada {BASE_INTERVAL_STR} para los últimos {dias} días...\n")

    while inicio < ahora:
        print(f"🔄 Desde: {inicio.isoformat()} UTC")
        datos = get_binance_klines(SYMBOL, BASE_INTERVAL_STR, inicio)
        if not datos:
            break
        todas_las_velas.extend(datos)
        ultima_vez = datetime.fromtimestamp(datos[-1][0] / 1000)
        inicio = ultima_vez + timedelta(milliseconds=1)
        time.sleep(0.5)

    if not todas_las_velas:
        print("⚠️ No se descargaron datos. Revisa la conexión o los parámetros.")
        return pd.DataFrame()

    df = pd.DataFrame(todas_las_velas, columns=[
        "timestamp", "Open", "High", "Low", "Close", "Volume",
        "Close_time", "Quote_asset_volume", "Number_of_trades",
        "Taker_buy_base", "Taker_buy_quote", "Ignore"
    ])
    df = df[["timestamp", "Open", "High", "Low", "Close", "Volume"]]  # solo las columnas que usas
    df = df.astype({"Open": float, "High": float, "Low": float, "Close": float, "Volume": float})
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit='ms')
    df["timestamp"] = df["timestamp"].dt.tz_localize("UTC").dt.tz_convert(tz_local)
    df.set_index("timestamp", inplace=True)

    df.to_csv(ruta_salida)
    print(f"\n✅ Velas guardadas en: {ruta_salida}  ({len(df)} filas)")
    return df


if __name__ == "__main__":
    descargar_velas(dias=10)
