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
from utils.patrones import determinar_patron_dominante
from utils.binance_data import obtener_vela_en_formacion, actualizar_datos

tz_local = pytz.timezone(TIMEZONE)

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
            
            linea1 = f"⏱️   {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} — Analizando vela cerrada + en formación"
            linea1 += f" | Posible: {patron}" if patron else "..."
            linea2 = f"📍 Vela en formación: Open={vela['Open']} | High={vela['High']} | Low={vela['Low']} | Close={vela['Close']} | Volume={vela['Volume']}"

            # Mueve cursor 2 líneas arriba, borra, luego imprime ambas líneas
            sys.stdout.write("\033[F\033[K" * 2)  # ANSI: cursor arriba y borra línea (x2)
            print(linea1)
            print(linea2)




        time.sleep(1)
