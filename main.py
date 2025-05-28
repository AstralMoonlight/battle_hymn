# main.py

import time
import sys
from datetime import datetime
from config import ANALYSIS_INTERVAL
from utils.binance_data import actualizar_datos, obtener_klines, set_symbol
from utils.resample import resamplear
from utils.indicadores import calcular_indicadores
from utils.consola import mostrar_ultimo
from utils.estrategia import evaluar_senal
from utils.patrones import determinar_patron_dominante
from utils.binance_data import obtener_vela_en_formacion, actualizar_datos



def esperar_nueva_vela(ultimo_timestamp):
    print("⏳ Esperando nueva vela...")
    primera_iteracion = True
    while True:
        df = obtener_klines()
        df_resampled = resamplear(df, ANALYSIS_INTERVAL)
        nueva_ultima = df_resampled.index[-1]
        if nueva_ultima > ultimo_timestamp:
            print("\n")
            return df
        vela = obtener_vela_en_formacion()
        vela_anterior = df.iloc[-1]
        patron = determinar_patron_dominante(vela_anterior, vela)
        linea1 = f"⏱️   {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} — Analizando vela cerrada + en formación"
        linea1 += f" | Posible: {patron}" if patron else "..."
        linea2 = f"📍 Vela en formación: Open={vela['Open']} | High={vela['High']} | Low={vela['Low']} | Close={vela['Close']} | Volume={vela['Volume']}"
        if not primera_iteracion:
            sys.stdout.write("\033[F\033[K" * 2)
        print(linea1)
        print(linea2)
        primera_iteracion = False
        time.sleep(5)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("⚠️ Debes indicar un símbolo. Ejemplo: python main.py BTCUSDT")
        sys.exit(1)

    symbol = sys.argv[1].upper()
    set_symbol(symbol)

    print(f"📈 Iniciando monitoreo para {symbol}...\n")

    while True:
        df_actual = actualizar_datos()
        df_resampled = resamplear(df_actual, ANALYSIS_INTERVAL)
        df_final = calcular_indicadores(df_resampled)
        mostrar_ultimo(df_final,symbol)
        evaluar_senal(df_final)
        ultima_ts = df_final.index[-1]
        df_espera = esperar_nueva_vela(ultima_ts)
        