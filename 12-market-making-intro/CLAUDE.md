# Clase 12 — Market making — Intro (guía de implementación)

Pieza del framework: **MarketMaker: cotizar a ambos lados y gestionar inventario**.

## Teoría que cubre

El otro lado del mercado: el **market maker** cotiza bid y ask y gana el **spread**. Su
enemigo es el **inventario**: si el flujo es desequilibrado acumula posición justo cuando el
mercado va en su contra (**adverse selection**).

Aparece la **utilidad CARA** `-e^{-γW}` y el parámetro de **aversión al riesgo** γ. La primera
defensa es el **skew por inventario**: el *reservation price* = `mid - skew·inventario` baja
ambas cotizaciones cuando estás largo, para que te compren menos y te vendan más y vuelvas a
plano.

## Implementación técnica

`exchange/strategies/market_maker.py` (`MarketMaker`): `quotes(book) -> (bid, ask)` en torno
al `reservation_price`, `on_fill` actualiza el inventario interno. Y `exchange/simulation.py`
(`MMSimulation`): como una limit no se cruza en el replay de snapshots, el market making se
simula contra un mid en paseo aleatorio con **modelo de intensidad de fills**
`λ(δ) = A·e^{-κδ}` (más cerca del mid, más probable que te ejecuten).

## Presentación (3 bloques)

1. **De dónde sale el PnL** — Compras en el bid, vendes en el ask, te quedas el spread. Si el flujo es equilibrado, ganas en cada vuelta. El problema es cuando no lo es.
2. **Riesgo de inventario y adverse selection** — Si solo te compran (te quedas corto) o solo te venden (te quedas largo), acumulas posición justo cuando el mercado va en tu contra. Eso es adverse selection.
3. **Skew por inventario** — La defensa: cuando estás largo, baja tus dos cotizaciones para que te compren menos y te vendan más, y vuelvas a plano. El reservation price hace justo eso.

## Cuaderno de construcción

Patrón por ejercicio: enunciado → starter (`pass`/`None`) → validador (`assert` con mensaje claro, tolerancia `1e-9`) → solución guiada embebida.
Tiers: **Núcleo** = ej. 1-3 (en clase), **Si vamos bien** = resto, **Auxiliares** = cuaderno `12_auxiliary.ipynb`.

El contenido se genera desde `framework/_build/` — para editar esta clase, edita su spec y regenera con `build_course.py`. No edites a mano los notebooks.

## Continuidad

El paquete `exchange/` llega con lo construido hasta la clase anterior; hoy se añade la pieza nueva, que se convierte en el starter de la siguiente.
