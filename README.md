source venv/Scripts/activate
python -m venv venv

pip freeze > requirements.txt
pip install -r requirements.txt


### “Prompt de Mejora” — Entregable para mañana

*(Copia y pega tal cual en tu README o en un issue de GitHub; deleita a tu “yo futuro” con instrucciones claras y sin vendettas nocturnas).*

---

## 1. Objetivo claro

> **Meta realista:** alcanzar un **Profit Factor ≥ 1.5** y **Drawdown máx ≤ 15 %** durante 90 días de backtest.
> El 4 % diario vendrá por rachas; la solidez estadística es el verdadero Santo Grial.

---

## 2. Checklist de cirugía al archivo `evaluar_senal.py`

1. **Cruces genuinos, no estados eternos**

   ```python
   cruza_sma   = df["SMA9"].iloc[-2] <= df["SMA20"].iloc[-2] and sma9 > sma20
   cruza_di    = df["+DI"].iloc[-2]  <= df["-DI"].iloc[-2]  and plus_di > minus_di
   ```

   * **LONG** exige `cruza_sma` **o** `cruza_di` (elige la que mejor rinda).
   * Esto evita disparar señales en cada vela.

2. **`diferencia_di` dinámica**

   * Sustituir el fijo `1` por **percentil 60** de la serie |DI+ − DI−| en las últimas 100 velas.
   * Ejemplo:

     ```python
     diff_threshold = df["|DI_gap|"].rolling(100).quantile(0.60).iloc[-1]
     ```

3. **ADX con pendiente positiva**

   ```python
   adx_ok = adx > 22 and adx > df["ADX"].iloc[-2]
   ```

4. **Filtro RSI**

   * LONG: `rsi > 55` **y** `rsi_slope = rsi - df["RSI"].iloc[-3] > 0`.
   * SHORT inverso.

5. **Bollinger coherente**

   * Si buscas rebote: LONG solo si `Close < BB_Media`.
   * Si buscas tendencia: LONG solo si `Close > BB_Media`.
   * **Define uno**, no ambos.

6. **Gestión de riesgo ATR**

   ```python
   atr = df["ATR14"].iloc[-1]
   SL  = 1.0 * atr
   TP  = 1.5 * atr
   ```

   * Con apalancamiento 5-10×, mantén **riesgo real = 2 %** del equity por trade.

7. **Comisiones & funding**

   * Resta 0.05 % (taker) por entrada y salida.
   * Simula funding −0.04 % cada 8 h.

8. **Control de “una sola operación”**

   * Flag global `operacion_activa`; ignora nuevas señales hasta que se cierre con TP/SL.

9. **Walk-forward (no al curve fitting)**

   * Optimiza en 01-Jan→31-Mar 2024.
   * Valida en 01-Apr→30-Jun 2024.
   * Restaura variables default y re-testea Jul-Sep 2024.

10. **Logging & métricas extra**

    ```
    trade_id | timestamp | side | entry | exit | pnl% | fee | cause (TP/SL/close)
    ```

    * Genera CSV para análisis; calcula Profit Factor, Sharpe, Max DD.

---

## 3. Secuencia de implementación

1. **Refactor**

   * Mueve la lógica de señales a `signal_engine/di_sma_strategy.py`.
   * Crea módulo `risk.py` con funciones `calcular_sl_tp()` y `calcular_size()`.

2. **Prueba unitaria rápida**

   * Ejecuta backtest **sin leverage** sobre 90 días.
   * Meta: PF > 1.2; si no, re-afina umbrales.

3. **Añade leverage 5×**

   * Re-ejecuta. Observa si DD escala proporcionalmente (<25 %).
   * Solo entonces prueba 10×.

4. **Documenta**

   ```markdown
   ## Estrategia DI-SMA v2
   - Cruce SMA9/20 + filtro DI/ADX/RSI
   - TP = 1.5 ATR, SL = 1.0 ATR
   - Fees y funding incluidos
   ```

   * Incluye resultados (tabla métricas + curva de equity).

5. **Validación final**

   * Test out-of-sample Oct-Nov 2024.
   * Si PF ≥ 1.5 y DD ≤ 15 %, ¡promoción a entorno en vivo (paper-trading) 2 semanas!

---

## 4. Recordatorio zen

> “El bot perfecto no busca adivinar el futuro; solo *gestiona* el presente mejor que sus rivales.”
> — Sun-Tzu, versión cripto.

Guarda este prompt junto a tu código y conviértelo en *issue* o *milestone* para que mañana sea tu mapa de ruta.
