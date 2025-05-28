# utils/patrones.py

from utils.patrones_velas import *

def determinar_patron_dominante(vela_anterior, vela):
    if es_estrella_amanecer(vela_anterior, vela):
        return "🌅 Estrella del amanecer: Posible reversión alcista"
    elif es_estrella_atardecer(vela_anterior, vela):
        return "🌇 Estrella del atardecer: Posible reversión bajista"
    elif es_harami_alcista(vela_anterior, vela):
        return "🟢 Harami alcista: Posible reversión alcista"
    elif es_harami_bajista(vela_anterior, vela):
        return "🔻 Harami bajista: Posible reversión bajista"
    elif es_hammer(vela):
        return "🔨 Hammer: Posible rebote alcista tras caída"
    elif es_hanging_man(vela):
        return "🚨 Hanging Man: Advertencia de reversión bajista"
    elif es_inverted_hammer(vela):
        return "🪓 Inverted Hammer: Posible reversión alcista"
    elif es_shooting_star(vela):
        return "🌠 Shooting Star: Posible reversión bajista"
    elif es_doji(vela):
        return "⚠️ Doji: Señal de indecisión"
    return None