#!/usr/bin/env python3
"""
mass_test_v2.py — Grid search rápido *sin* descargas repetidas
"""

from __future__ import annotations
import itertools, importlib, os
from datetime import datetime

import pandas as pd
import config
import runBacktest

# ── 1. cache único de velas ──────────────────────────────────────────────
df_cache = runBacktest._asegurar_datos(config.SYMBOL, "1m", 10000)
df_cache = df_cache.sort_index().pipe(runBacktest.calcular_indicadores)

def _asegurar_datos_mock(*_a, **_k):
    return df_cache.copy()

runBacktest._asegurar_datos = _asegurar_datos_mock  # fija cache
# (opcional) silenciar prints de _asegurar_datos
runBacktest.print = lambda *a, **k: None

# ── 2. construir grid de parámetros ─────────────────────────────────────
def lst_or_default(name, default):
    lst = getattr(config, f"{name}_LIST", [])
    return lst if isinstance(lst, (list, tuple)) and len(lst) > 1 else [default]

grid = {
    "RSI_CORTE":     lst_or_default("RSI_CORTE",     config.RSI_CORTE),
    "ADX_THRESHOLD": lst_or_default("ADX_THRESHOLD", config.ADX_THRESHOLD),
    "DI_PERCENTILE": lst_or_default("DI_PERCENTILE", config.DI_PERCENTILE),
    "DI_WINDOW":     lst_or_default("DI_WINDOW",     config.DI_WINDOW),
    "TP":            lst_or_default("TP",            config.TP),
    "SL":            lst_or_default("SL",            config.SL),
}
grid = {k: v for k, v in grid.items() if len(v) > 1}
combos = list(itertools.product(*grid.values()))
print(f"🧪 Total combinaciones: {len(combos)}\n")

# ── 3. backtests ─────────────────────────────────────────────────────────
results = []
for i, combo in enumerate(combos, 1):
    for k, v in zip(grid.keys(), combo):
        setattr(config, k, v)

    importlib.reload(runBacktest)                    # recarga lógica
    runBacktest._asegurar_datos = _asegurar_datos_mock  # <- re-fija cache

    res = runBacktest.run_backtest(config.SYMBOL, "5m", 5000)
    if not res:
        continue

    wins, losses = res["Ganadoras"], res["Perdedoras"]
    pf       = (wins if wins else 1) / (losses if losses else 1)
    win_pct  = wins / res["Operaciones"] * 100 if res["Operaciones"] else 0

    res.update({k: v for k, v in zip(grid.keys(), combo)})
    res.update({"Win %": round(win_pct, 2), "ProfitFactor": round(pf, 2)})
    results.append(res)

    print(f"✅ {i:4}/{len(combos)} | PnL={res['Rentabilidad (%)']:+6.2f}% | "
          f"Ops={res['Operaciones']:3} | Win%={win_pct:5.1f} | PF={pf:4.2f}")

# ── 4. guardar CSV y mostrar Top-10 ──────────────────────────────────────
df = pd.DataFrame(results).sort_values("ProfitFactor", ascending=False)
os.makedirs("results", exist_ok=True)
csv_path = f"results/grid_{datetime.now():%Y%m%d_%H%M%S}.csv"
df.to_csv(csv_path, index=False)

print("\n🏆 TOP-10 por ProfitFactor")
print(df.head(10).to_string(index=False))
print(f"\n📁 CSV completo en {csv_path}")
