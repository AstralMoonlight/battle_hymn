# realtime_binance.py
import time
from config import ANALYSIS_INTERVAL
from utils.binance_data import actualizar_datos, obtener_klines
from utils.resample import resamplear
from utils.indicadores import calcular_indicadores
from utils.consola import mostrar_ultimo
from utils.estrategia import evaluar_senal


def esperar_nueva_vela(ultimo_timestamp):
    print("⏳ Esperando nueva vela...")
    while True:
        df = obtener_klines()
        df_resampled = resamplear(df, ANALYSIS_INTERVAL)
        nueva_ultima = df_resampled.index[-1]
        if nueva_ultima > ultimo_timestamp:
            return df
        time.sleep(1)

if __name__ == "__main__":
    while True:
        df_actual = actualizar_datos()
        df_resampled = resamplear(df_actual, ANALYSIS_INTERVAL)
        df_final = calcular_indicadores(df_resampled)
        mostrar_ultimo(df_final)
        evaluar_senal(df_final)
        ultima_ts = df_final.index[-1]
        df_espera = esperar_nueva_vela(ultima_ts)
