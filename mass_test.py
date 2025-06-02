# mass_test.py

"""
Script para pruebas masivas usando grid_config.py:
- Itera sobre todos los valores de RSI_CORTE, ADX_THRESHOLD, DIFERENCIA_DI,
  TP, SL, así como sobre intervalos, total_candles y (opcionalmente) SMAs.
- Para cada combinación, modifica config.py en tiempo de ejecución,
  ejecuta run_backtest(...) y almacena los resultados en una lista.
- Al final muestra un resumen por pantalla y guarda un CSV con todo.
"""

import pandas as pd
import config
import grid_config   # Importa las listas definidas en grid_config.py
from runBacktest import run_backtest

# Listas principales a iterar
SYMBOL_LIST        = grid_config.SYMBOL_LIST
INTERVAL_LIST      = grid_config.INTERVAL_LIST
TOTAL_CANDLES_LIST = grid_config.TOTAL_CANDLES_LIST
RSI_list           = grid_config.RSI_CORTE_LIST
ADX_list           = grid_config.ADX_THRESHOLD_LIST
DI_list            = grid_config.DIFERENCIA_DI_LIST

# Nuevas listas para TP y SL
TP_list = grid_config.TP_LIST
SL_list = grid_config.SL_LIST

# (Opcional) Si quieres variar SMAs:
# SMA_fast_list = grid_config.SMA_CORTA_LIST
# SMA_slow_list = grid_config.SMA_LARGA_LIST

resultados = []

if __name__ == "__main__":
    for symbol in SYMBOL_LIST:
        # Asignar símbolo en config para los prints
        config.SYMBOL = symbol

        for interval in INTERVAL_LIST:
            for total in TOTAL_CANDLES_LIST:
                for rsi_val in RSI_list:
                    for adx_val in ADX_list:
                        for dif_val in DI_list:
                            for tp_val in TP_list:
                                for sl_val in SL_list:
                                    # (Opcional) si iteras SMAs, anida aquí:
                                    # for sma_fast in SMA_fast_list:
                                    #     for sma_slow in SMA_slow_list:
                                    #         config.SMA_CORTA = sma_fast
                                    #         config.SMA_LARGA = sma_slow

                                    # Sobrescribir valores en config
                                    config.RSI_CORTE     = rsi_val
                                    config.ADX_THRESHOLD = adx_val
                                    config.DIFERENCIA_DI = dif_val
                                    config.TP            = tp_val
                                    config.SL            = sl_val

                                    etiqueta = (
                                        f"SYMBOL={symbol}, "
                                        f"INTERVAL={interval}, "
                                        f"TOTAL={total}, "
                                        f"RSI={rsi_val}, "
                                        f"ADX={adx_val}, "
                                        f"DIF_DI={dif_val}, "
                                        f"TP={tp_val}%, "
                                        f"SL={sl_val}%"
                                    )
                                    print("\n" + "="*70)
                                    print(f">>> Iniciando prueba: {etiqueta}")
                                    print("="*70 + "\n")

                                    # Ejecutar backtest y capturar métricas
                                    metrics = run_backtest(symbol, interval, total)

                                    if metrics:
                                        # Agregar parámetros al diccionario de métricas
                                        metrics["Symbol"]        = symbol
                                        metrics["Interval"]      = interval
                                        metrics["Total_Candles"] = total
                                        metrics["RSI_CORTE"]     = rsi_val
                                        metrics["ADX_THRESHOLD"] = adx_val
                                        metrics["DIFERENCIA_DI"]  = dif_val
                                        metrics["TP (%)"]        = tp_val
                                        metrics["SL (%)"]        = sl_val
                                        resultados.append(metrics)
                                    else:
                                        print(f"⚠️ No se obtuvieron métricas para: {etiqueta}")

    # Construir DataFrame si hay resultados
    if resultados:
        df_summary = pd.DataFrame(resultados)

        # Mostrar por pantalla (sin índices para legibilidad)
        print("\n" + "*"*70)
        print("Resumen de todas las combinaciones probadas:\n")
        print(df_summary.to_string(index=False))
        print("*"*70 + "\n")

        # Guardar a CSV
        csv_path = "resumen_pruebas_masivas.csv"
        df_summary.to_csv(csv_path, index=False)
        print(f"✅ Resumen completo guardado en: {csv_path}")
    else:
        print("⚠️ No se recolectaron resultados (quizá hubo errores o data vacía).")
