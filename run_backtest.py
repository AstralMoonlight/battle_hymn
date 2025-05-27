# run_backtest.py

from config import DIAS_TEST, SALDO_INICIAL, APALANCAMIENTO, TP, SL
from utils.binance_data import cargar_datos_locales
from utils.resample import resamplear
from utils.indicadores import calcular_indicadores
from utils.estrategia import evaluar_senal
from backtest.simulador import simular_operaciones

# Carga datos y recorta a los últimos N días
df = cargar_datos_locales()
df = resamplear(df, "1min")
df = calcular_indicadores(df)
df = df.last(f"{DIAS_TEST}D")

# Variables de simulación
saldo = SALDO_INICIAL
operacion_activa = False
tipo_operacion = None
entrada = 0

print("🔁 Ejecutando backtest...\n")
simular_operaciones(df)

for i in range(1, len(df)):
    fila = df.iloc[i]
    fecha = df.index[i].strftime('%Y-%m-%d %H:%M:%S')
    precio = fila["Close"]

    # Si hay una operación abierta, revisar si debe cerrarse
    if operacion_activa:
        variacion_pct = ((precio - entrada) / entrada) * 100
        variacion_pct *= APALANCAMIENTO
        if tipo_operacion == "short":
            variacion_pct *= -1  # Inverso para short

        print(f"🕒 {fecha} | ACTIVA: {tipo_operacion.upper()} | Entrada: {entrada:.2f} | P/L: {variacion_pct:.2f}%")

        if variacion_pct >= TP or variacion_pct <= SL:
            ganancia = saldo * (variacion_pct / 100)
            saldo += ganancia
            print(f"✅ CIERRE {tipo_operacion.upper()} | Saldo: {saldo:.2f} USDT | P/L: {variacion_pct:.2f}%")
            operacion_activa = False  # Libera para siguiente entrada
        continue  # Si hay operación, no se evalúa señal nueva

    # Si no hay operación activa, evaluar si hay señal
    fila_df = df.iloc[:i+1]
    senal = evaluar_senal(fila_df, solo_tipo=True)

    if senal:
        tipo_operacion = senal
        entrada = precio
        operacion_activa = True
        print(f"📈 ENTRADA {tipo_operacion.upper()} | {fecha} | Precio: {entrada:.2f}")

# Resultado final
print("\n📊 RESULTADOS BACKTEST:")
print(f"\n💰 Saldo final: {saldo:.2f} USDT")
