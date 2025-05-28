# run_backtest.py

from config import DIAS_TEST, SALDO_INICIAL, APALANCAMIENTO, TP, SL, CONFIRMACION_AVISO

from utils.binance_data import cargar_datos_locales
from utils.resample import resamplear
from utils.indicadores import calcular_indicadores
from utils.estrategia import evaluar_senal
from backtest.simulador import simular_operaciones
from datetime import timedelta


saldo = SALDO_INICIAL
operacion_activa = False
tipo_operacion = None
entrada = 0


# Estadísticas
longs = 0
shorts = 0
ganadoras = 0
perdedoras = 0
operaciones = 0



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

# Control de última entrada por tipo
ultima_entrada = {
    "long": None,
    "short": None
}
cooldown = timedelta(minutes=10)

print("🔁 Ejecutando backtest...\n")
simular_operaciones(df)

senal_contador = {
    "long": 0,
    "short": 0
}


for i in range(1, len(df)):
    fila = df.iloc[i]
    fecha = df.index[i]
    precio = fila["Close"]
    fecha_str = fecha.strftime('%Y-%m-%d %H:%M:%S')

    # Si hay una operación abierta, revisar si debe cerrarse
    if operacion_activa:
        variacion_pct = ((precio - entrada) / entrada) * 100
        variacion_pct *= APALANCAMIENTO
        if tipo_operacion == "short":
            variacion_pct *= -1  # Inverso para short

        print(f"🕒 {fecha_str} | ACTIVA: {tipo_operacion.upper()} | Entrada: {entrada:.2f} | P/L: {variacion_pct:.2f}%")

        if variacion_pct >= TP or variacion_pct <= SL:
            ganancia = saldo * (variacion_pct / 100)
            saldo += ganancia
            operaciones += 1
            if variacion_pct > 0:
                ganadoras += 1
            else:
                perdedoras += 1
            if tipo_operacion == "long":
                longs += 1
            else:
                shorts += 1
            print(f"✅ CIERRE {tipo_operacion.upper()} | Saldo: {saldo:.2f} USDT | P/L: {variacion_pct:.2f}%")
            operacion_activa = False
        continue

    # Evaluar señal solo si no hay operación activa
    fila_df = df.iloc[:i+1]
    senal = evaluar_senal(fila_df, solo_tipo=True)

    if senal:
        ultima = ultima_entrada.get(senal)
        if ultima is not None and (fecha - ultima) < cooldown:
            tiempo_restante = (cooldown - (fecha - ultima)).seconds // 60
            print(f"⛔ {fecha_str} | Ignorada señal {senal.upper()} (esperando {tiempo_restante} min)")
            continue

        # Incrementar confirmación para la señal detectada
        senal_contador[senal] += 1
        restantes = CONFIRMACION_AVISO - senal_contador[senal]

        if senal_contador[senal] >= CONFIRMACION_AVISO:
            tipo_operacion = senal
            entrada = precio
            operacion_activa = True
            ultima_entrada[senal] = fecha
            senal_contador[senal] = 0  # Reset al confirmar
            print(f"📈 ENTRADA CONFIRMADA {tipo_operacion.upper()} | {fecha_str} | Precio: {entrada:.2f}")
        else:
            print(f"👀 {fecha_str} | Señal {senal.upper()} detectada ({senal_contador[senal]}/{CONFIRMACION_AVISO}). Faltan {restantes} confirmaciones...")

        # Reiniciar el contador de la otra señal (opuesta)
        otro_tipo = "short" if senal == "long" else "long"
        senal_contador[otro_tipo] = 0
            
# Resultado final
rentabilidad = ((saldo / SALDO_INICIAL) - 1) * 100
print("\n📊 RESULTADOS BACKTEST:\n")
print(f"🔁 Operaciones ejecutadas: {operaciones}")
print(f"🟢 Longs: {longs}     🔴 Shorts: {shorts}")
print(f"✅ Ganadoras: {ganadoras} ❌ Perdedoras: {perdedoras}\n")
print(f"💰 Saldo inicial: {SALDO_INICIAL:.2f} USDT")
print(f"💵 Saldo final  : {saldo:.2f} USDT")
print(f"📈 Rentabilidad : {rentabilidad:.2f}%")
