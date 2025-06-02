# config.py
from binance.client import Client  # type: ignore

# === Parámetros de trading ===
SYMBOL = "BTCUSDT"
# Puedes cambiar a:
# SYMBOL = "ETHUSDT"
# SYMBOL = "ADAUSDT"

BASE_INTERVAL = Client.KLINE_INTERVAL_1MINUTE
BASE_INTERVAL_STR = "1m"         # Para uso en strings y rutas
ANALYSIS_INTERVAL = "1min"       # Para resampleo u otras funciones

TP = 4                           # Take Profit en porcentaje
SL = -10                         # Stop Loss en porcentaje negativo

LIMIT = 1000                    # Límite de velas por solicitud (máximo permitido por Binance)

SALDO_INICIAL = 200             # Capital inicial para backtest
APALANCAMIENTO = 15             # Leverage (apalancamiento)
DIAS_TEST = 3                   # Cuántos días usar en backtest

# === Archivo CSV por defecto (puede cambiarse si cambias SYMBOL) ===
CSV_FILE = f"data/{SYMBOL}_{BASE_INTERVAL_STR}.csv"

# === Zona horaria local para Chile Continental (con horario de verano automático) ===
TIMEZONE = "America/Santiago"

# === Confirmación de señales antes de ejecutar una orden (por ejemplo, 3 velas seguidas) ===
CONFIRMACION_AVISO = 2


# -------------
# Umbrales para estrategia
RSI_CORTE = 50
ADX_THRESHOLD = 22
DIFERENCIA_DI = 1
SMA_CORTA = 9     # número de periodos de la sma “rápida”
SMA_LARGA = 20    # número de periodos de la sma “lenta”


# ---------------------------------------------------
# **Nuevas listas** para pruebas masivas:
# Cada lista contendrá los valores que quieras testear
RSI_CORTE_LIST     = [45, 50, 55]
ADX_THRESHOLD_LIST = [20, 22, 25]
DIFERENCIA_DI_LIST = [1, 2, 3]

# (Si en el futuro quieres variar los periodos de SMA, podrías agregar:)
# SMA_CORTA_LIST = [5, 9, 14]
# SMA_LARGA_LIST = [20, 30, 50]
# ---------------------------------------------------