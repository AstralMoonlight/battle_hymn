# grid_config.py

"""
Este archivo contiene todas las listas de valores que se utilizarán
en mass_test.py para iterar combinaciones:
  - intervalos de vela
  - tamaños de muestra (número de velas)
  - umbrales RSI, ADX, diferencia de DI
  - periodos de SMA
  - valores de TP y SL
"""

# --- Símbolos a probar (puedes agregar más) ---
SYMBOL_LIST = ["BTCUSDT"]   # si en el futuro quieres probar ETHUSDT, LTCUSDT, etc.

# --- Intervalos de velas a iterar ---
# Binance soporta: "1m","3m","5m","15m","30m","1h","2h","4h","6h","8h","12h","1d","3d","1w","1M"
INTERVAL_LIST = ["5m", "15m", "30m", "1h"]

# --- Cantidad de velas a descargar / usar en el backtest ---
# Desde 500 hasta 2999 velas
TOTAL_CANDLES_LIST = list(range(500, 3000))

# --- Umbrales de RSI para probar ---
RSI_CORTE_LIST = [45, 50, 55]

# --- Umbrales de ADX para probar ---
# Desde 2 hasta 29
ADX_THRESHOLD_LIST = list(range(2, 30))

# --- Diferencia mínima entre +DI y -DI ---
DIFERENCIA_DI_LIST = list(range(1, 10))

# --- Periodos de las medias móviles simples para probar ---
SMA_CORTA_LIST = [5, 9, 14]
SMA_LARGA_LIST = [20, 30, 50, 100, 200]

# --- Valores de Take Profit (TP) en porcentaje para probar ---
# Por ejemplo, desde 2% hasta 10%
TP_LIST = list(range(2, 11))   # [2,3,4,5,6,7,8,9,10]

# --- Valores de Stop Loss (SL) en porcentaje para probar ---
# Por ejemplo, desde 1% hasta 5%
SL_LIST = list(range(1, 6))    # [1,2,3,4,5]
