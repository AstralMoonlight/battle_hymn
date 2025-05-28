# utils/vela_live.py

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import time
import requests
import pandas as pd
from datetime import datetime
from config import SYMBOL, BASE_INTERVAL_STR, TIMEZONE
import pytz
from utils.patrones_velas import *
from utils.binance_data import obtener_vela_en_formacion, actualizar_datos

tz_local = pytz.timezone(TIMEZONE)

def determinar_patron_dominante(vela_anterior, vela):
    if es_estrella_amanecer(vela_anterior, vela):
        return "🌅 Estrella del amanecer"
    elif es_estrella_atardecer(vela_anterior, vela):
        return "🌇 Estrella del atardecer"
    elif es_harami_alcista(vela_anterior, vela):
        return "🟢 Harami alcista"
    elif es_harami_bajista(vela_anterior, vela):
        return "🔻 Harami bajista"
    elif es_hammer(vela):
        return "🔨 Hammer"
    elif es_inverted_hammer(vela):
        return "🪓 Inverted Hammer"
    elif es_doji(vela):
        return ("⚠️" + "Doji")
    return None

if __name__ == "__main__":
    while True:
        df = actualizar_datos()
        if df.empty or len(df) < 1:
            print("⏳ Esperando velas válidas...")
            time.sleep(5)
            continue

        vela_anterior = df.iloc[-1]
        vela = obtener_vela_en_formacion()

        if vela is not None and not vela.empty and vela_anterior is not None:
            patron = determinar_patron_dominante(vela_anterior, vela)
            if patron:
                print(f"⏱️   {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} — Analizando vela cerrada + en formación | Posible: {patron}")
            else:
                print(f"⏱️   {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} — Analizando vela cerrada + en formación...")
            print(f"📍 Vela en formación: Open={vela['Open']} | High={vela['High']} | Low={vela['Low']} | Close={vela['Close']} | Volume={vela['Volume']}")
            print("-" * 80)
            print("\n")




        time.sleep(5)
