# backtest/simulador.py

from config import SALDO_INICIAL, APALANCAMIENTO, SL, TP
from utils.estrategia import evaluar_senal
import pandas as pd

def ejecutar_backtest(df):
    operacion_activa = False
    saldo = SALDO_INICIAL
    entrada = 0
    fecha_entrada = None
    tipo_operacion = None  # "long" o "short"
    resultado_dias = []

    df = df.copy()

    for i in range(1, len(df)):
        fila = df.iloc[i]
        fecha = fila.name.strftime('%Y-%m-%d %H:%M:%S')

        # Abrir operación si no hay ninguna activa
        if not operacion_activa:
            señal = evaluar_senal(df.iloc[:i+1], solo_tipo=True)
            if señal in ("long", "short"):
                operacion_activa = True
                entrada = fila["Close"]
                fecha_entrada = fecha
                tipo_operacion = señal
                print(f"🟢 {fecha} | Entrada {tipo_operacion.upper()} en {entrada:.2f}")
                continue

        # Si hay una operación activa, verificar SL / TP
        if operacion_activa:
            precio_actual = fila["Close"]
            variacion = (precio_actual - entrada) / entrada if tipo_operacion == "long" else (entrada - precio_actual) / entrada
            variacion_pct = variacion * 100

            if variacion_pct >= TP or variacion_pct <= SL:
                ganancia = saldo * (variacion * APALANCAMIENTO)
                saldo += ganancia
                resultado_dias.append({
                    "fecha": fecha_entrada,
                    "tipo": tipo_operacion,
                    "entrada": round(entrada, 2),
                    "salida": round(precio_actual, 2),
                    "variacion%": round(variacion_pct, 2),
                    "ganancia": round(ganancia, 2),
                    "saldo": round(saldo, 2)
                })
                print(f"🔴 {fecha} | Cierre {tipo_operacion.upper()} en {precio_actual:.2f} | Variación: {variacion_pct:.2f}% | Ganancia: {ganancia:.2f} | Saldo: {saldo:.2f}")
                operacion_activa = False
                tipo_operacion = None

        # Seguimiento de operación activa
        if operacion_activa:
            print(f"🕒 {fecha} | Operación activa: {tipo_operacion.upper()} | Entrada: {entrada:.2f}")

    # Mostrar resumen por consola si hubo operaciones
    if resultado_dias:
        df_resumen = pd.DataFrame(resultado_dias)
        print("\n📋 RESUMEN DE OPERACIONES:")
        print(df_resumen.to_string(index=False))

    return resultado_dias, saldo


def simular_operaciones(df):
    saldo = SALDO_INICIAL
    operacion = None
    operaciones_realizadas = []

    for i in range(len(df)):
        fila = df.iloc[i]
        timestamp = fila.name
        close = fila["Close"]

        if operacion:
            entrada = operacion["precio_entrada"]
            tipo = operacion["tipo"]
            variacion_pct = ((close - entrada) / entrada * 100) * (1 if tipo == "long" else -1)

            if variacion_pct >= TP or variacion_pct <= SL:
                resultado_pct = variacion_pct
                resultado_dinero = saldo * (resultado_pct / 100) * APALANCAMIENTO
                saldo += resultado_dinero
                operaciones_realizadas.append({
                    "fecha": timestamp.strftime("%Y-%m-%d %H:%M"),
                    "tipo": tipo,
                    "entrada": entrada,
                    "salida": close,
                    "resultado_pct": round(resultado_pct, 2),
                    "saldo": round(saldo, 2)
                })
                print(f"✅ Cierre {tipo.upper()} | Entrada: {entrada:.2f} → Salida: {close:.2f} | {resultado_pct:.2f}% | Saldo: {saldo:.2f}")
                operacion = None

        if not operacion:
            señal = evaluar_senal(df.iloc[:i+1], solo_tipo=True)
            if señal:
                operacion = {
                    "tipo": señal,
                    "precio_entrada": close
                }
                print(f"📥 Entrada {señal.upper()} en {close:.2f} ({timestamp.strftime('%Y-%m-%d %H:%M')})")

    # 📊 Resumen final
    print("\n📊 RESULTADOS BACKTEST:")
    print(f"\n🔁 Operaciones ejecutadas: {len(operaciones_realizadas)}")
    longs = sum(1 for o in operaciones_realizadas if o["tipo"] == "long")
    shorts = sum(1 for o in operaciones_realizadas if o["tipo"] == "short")
    ganadoras = sum(1 for o in operaciones_realizadas if o["resultado_pct"] > 0)
    perdedoras = sum(1 for o in operaciones_realizadas if o["resultado_pct"] < 0)
    print(f"🟢 Longs: {longs}     🔴 Shorts: {shorts}")
    print(f"✅ Ganadoras: {ganadoras} ❌ Perdedoras: {perdedoras}")
    rentabilidad = (saldo - SALDO_INICIAL) / SALDO_INICIAL * 100
    print(f"\n💰 Saldo inicial: {SALDO_INICIAL:.2f} USDT")
    print(f"💵 Saldo final  : {saldo:.2f} USDT")
    print(f"📈 Rentabilidad : {rentabilidad:.2f}%")
