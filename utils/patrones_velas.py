# utils/patrones_velas.py

def es_doji(vela):
    cuerpo = abs(vela["Close"] - vela["Open"])
    mecha_superior = vela["High"] - max(vela["Close"], vela["Open"])
    mecha_inferior = min(vela["Close"], vela["Open"]) - vela["Low"]
    return cuerpo < (mecha_superior + mecha_inferior) * 0.3

def es_hammer(vela):
    cuerpo = abs(vela["Close"] - vela["Open"])
    mecha_inferior = min(vela["Close"], vela["Open"]) - vela["Low"]
    return mecha_inferior > cuerpo * 2 and vela["Close"] > vela["Open"]

def es_hanging_man(vela):
    cuerpo = abs(vela["Close"] - vela["Open"])
    mecha_inferior = min(vela["Close"], vela["Open"]) - vela["Low"]
    return mecha_inferior > cuerpo * 2 and vela["Close"] < vela["Open"]

def es_inverted_hammer(vela):
    cuerpo = abs(vela["Close"] - vela["Open"])
    mecha_superior = vela["High"] - max(vela["Close"], vela["Open"])
    return mecha_superior > cuerpo * 2 and vela["Close"] < vela["Open"]

def es_shooting_star(vela):
    cuerpo = abs(vela["Close"] - vela["Open"])
    mecha_superior = vela["High"] - max(vela["Close"], vela["Open"])
    return mecha_superior > cuerpo * 2 and vela["Close"] < vela["Open"]


def es_harami_alcista(vela_anterior, vela):
    return (
        vela_anterior["Close"] < vela_anterior["Open"] and
        vela["Close"] > vela["Open"] and
        vela["Open"] > vela_anterior["Close"] and
        vela["Close"] < vela_anterior["Open"]
    )

def es_harami_bajista(vela_anterior, vela):
    return (
        vela_anterior["Close"] > vela_anterior["Open"] and
        vela["Close"] < vela["Open"] and
        vela["Open"] < vela_anterior["Close"] and
        vela["Close"] > vela_anterior["Open"]
    )

def es_estrella_amanecer(vela_anterior, vela):
    return (
        vela_anterior["Close"] < vela_anterior["Open"] and
        vela["Open"] < vela_anterior["Close"] and
        vela["Close"] > vela_anterior["Open"]
    )

def es_estrella_atardecer(vela_anterior, vela):
    return (
        vela_anterior["Close"] > vela_anterior["Open"] and
        vela["Open"] > vela_anterior["Close"] and
        vela["Close"] < vela_anterior["Open"]
    )
