"""
config.py  —  Parámetros centralizados del bot Ioni
===================================================

Agrupados por secciones lógicas para facilitar ajustes y optimizaciones.
Cualquier módulo debe importar desde aquí; evita números “mágicos” en el código.
"""

# ───────────────────────────── Exchange & Símbolo ─────────────────────────────
from binance.client import Client  # type: ignore

SYMBOL             = "BTCUSDT"              # ← cambia aquí si usas ETHUSDT, etc.
BASE_INTERVAL      = Client.KLINE_INTERVAL_1MINUTE
BASE_INTERVAL_STR  = "1m"                   # para rutas y nombres de archivo
ANALYSIS_INTERVAL  = "1min"                 # resampleo interno
TIMEZONE           = "America/Santiago"     # zona horaria local
LIMIT_API          = 1000                   # máx. velas por request (Binance)

# CSV por defecto
CSV_FILE = f"data/{SYMBOL}_{BASE_INTERVAL_STR}.csv"

# ───────────────────────────── Money Management ───────────────────────────────
SALDO_INICIAL   = 200      # USDT
APALANCAMIENTO  = 10       # leverage
TP              = 4        # % take-profit
SL              = -5       # % stop-loss (negativo)
DIAS_TEST       = 15        # días a incluir en backtest
CONFIRMACION_AVISO = 2     # Nº de velas seguidas que confirman la señal

# ───────────────────────────── Indicadores base ───────────────────────────────
RSI_PERIOD  = 14
ADX_PERIOD  = 14
ATR_PERIOD  = 14
BB_PERIOD   = 20
BB_STD      = 2

# SMA (cálculo genérico - se pueden usar también SMA_MED, SMA_LONG, etc.)
SMA_CORTA = 9
SMA_LARGA = 20

# ───────────────────────────── Filtros de Estrategia ──────────────────────────
RSI_CORTE          = 50
ADX_THRESHOLD      = 20
DI_WINDOW          = 100      # nº velas para percentil DI
DI_PERCENTILE      = 0.60     # 0-1, define el umbral dinámico
ADX_SLOPE_LOOKBACK = 1        # velas para pendiente ADX
RSI_SLOPE_LOOKBACK = 3        # velas para pendiente RSI

# ───────────────────────────── Depuración / Sonidos ───────────────────────────
DEBUG_LEVEL  = 2              # 0 = off, 1 = señales, 2 = verbose
SONIDO_LONG  = "wav/sound2.wav"
SONIDO_SHORT = "wav/sound3.wav"

# ───────────────────────────── Listas para pruebas masivas ────────────────────
#  Añade valores aquí; tus scripts de grid/optimización iterarán sobre ellas.
RSI_CORTE_LIST       = [45, 50, 55]
ADX_THRESHOLD_LIST   = [18, 20, 22, 25]
DI_PERCENTILE_LIST   = [0.40, 0.50, 0.60, 0.70]
DI_WINDOW_LIST       = [50, 100, 150]
SMA_CORTA_LIST       = [5, 9, 14]
SMA_LARGA_LIST       = [20, 30, 50, 100, 200]
TP_LIST              = [3, 4, 5, 6]
SL_LIST              = [-5, -8, -10, -12]

# Nota: si alguna lista está vacía o falta, los scripts de optimización
#       simplemente usarán el valor único definido más arriba.
