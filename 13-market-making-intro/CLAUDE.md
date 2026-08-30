# Clase 13 — Market making — Intro (guía de implementación)

Pieza del framework: **MarketMaker: cotizar a ambos lados y gestionar inventario**.

## Teoría que cubre

El otro lado del mercado: el **market maker** cotiza bid y ask y gana el **spread**. Su
enemigo es el **inventario**: si el flujo es desequilibrado acumula posición justo cuando el
mercado va en su contra (**adverse selection**).

Aparece la **utilidad CARA** `-e^{-γW}` y el parámetro de **aversión al riesgo** γ. La primera
defensa es el **skew por inventario**: el *reservation price* = `mid - skew·inventario` baja
ambas cotizaciones cuando estás largo, para que te compren menos y te vendan más y vuelvas a
plano. CARA y la intuición de intensidad de fills forman un puente **LIVE** a γ/κ en
L14; la estrategia concreta y sus fórmulas no se exponen en L13.

## Implementación técnica

`exchange/strategies/market_maker.py` (`MarketMaker`): `quotes(book) -> (bid, ask)` en torno
al `reservation_price`, `on_fill` actualiza el inventario interno. Y `exchange/simulation.py`
(`MMSimulation`): el replay no contiene el flujo contrafactual que golpearía cada quote
pasiva, así que el market making se simula contra un mid en paseo aleatorio con **modelo de
intensidad de fills** `λ(δ) = A·e^{-κδ}` (más cerca del mid, más probable que te ejecuten).
Su `sigma` es la volatilidad de precio del horizonte completo y cada paso usa
`sigma/√steps`. El resultado cuenta fills y conserva series de inventario y PnL para
validar el feedback.

## Presentación (3 bloques)

1. **De dónde sale el PnL** — Compras en el bid, vendes en el ask, te quedas el spread. Si el flujo es equilibrado, ganas en cada vuelta.
2. **Riesgo de inventario y adverse selection** — Si solo te compran o solo te venden, acumulas posición justo cuando el mercado va en tu contra. Eso es adverse selection.
3. **Skew por inventario** — Cuando estás largo, baja tus dos cotizaciones para que te compren menos y te vendan más, y vuelvas a plano.
4. **Puente LIVE a L14: gamma y kappa** — CARA da significado a gamma como aversión al riesgo. La intensidad lambda(delta)=A*exp(-kappa*delta) explica por qué alejar una quote reduce sus fills y qué controla kappa. L13 fija estas dos intuiciones sin exponer la clase ni las fórmulas de L14.

## Cuaderno de construcción

Patrón por ejercicio: enunciado → starter (`pass`/`None`) → validador (`assert` con mensaje claro, tolerancia `1e-9`) → solución guiada embebida.
Clasificación: **LIVE / REQUIRED / OPTIONAL**, decidida en `pedagogy/exercise_routes.yml`. Auxiliares: `13_auxiliary.ipynb`.

El contenido se genera desde `framework/_build/` — para editar esta clase, edita su spec y regenera con `build_course.py`. No edites a mano los notebooks.

## Continuidad

El snapshot de `exchange/` declara exactamente la superficie disponible en L13. La lección construye su pieza sobre esa superficie; el snapshot siguiente conserva el estado acumulado sin presuponer que cada clase añada un módulo nuevo.
