# Clase 10 — VWAP I — Baselines de volumen

> Primer algoritmo de ejecución: repartir una orden grande en trozos a lo largo de la sesión. TWAP (uniforme) y VWAP (siguiendo el perfil de volumen) como baselines.

## Contexto teórico

Primer algoritmo de **ejecución**. Mandar una orden grande de golpe barre el libro y paga
impacto; **trocearla** en el tiempo lo reduce. Dos baselines:
- **TWAP** (time-weighted): trozos iguales en el tiempo. Honesto y difícil de batir sin info.
- **VWAP** (volume-weighted): pondera por el **perfil de volumen** intradía, para acercarse al
  precio medio ponderado por volumen — el benchmark estándar de ejecución institucional.

El perfil son pesos relativos: se normalizan, así que importan las proporciones, no la escala.

## Qué construyes hoy

**VWAPStrategy: repartir una orden por el perfil de volumen**

`exchange/strategies/vwap.py` (`VWAPStrategy(symbol, side, total_size, horizon, profile)`):
en cada tick emite una market order del tamaño del trozo (peso normalizado × total). Sin
perfil → TWAP uniforme. Es una subclase de `Strategy`: se enchufa al `Backtest` exactamente
igual que cualquier otra — primera demostración del valor del framework de L8.

## Ejercicios de construcción

- **1. Schedule TWAP** — pesos uniformes
- **2. Lanza un VWAPStrategy** — estrategia de ejecución
- **3. Perfil VWAP a medida** — pasar un perfil
- **4. Precio medio de ejecución** — VWAP de tus fills

## Estructura de la carpeta

- `presentation/` — presentación interactiva + guion del profesor
- `exercises/10_build_exercises.ipynb` — construyes la pieza (núcleo 1-3, luego el resto)
- `exercises/10_auxiliary.ipynb` — profundización opcional
- `exercises/exchange/` — el paquete que vienes construyendo (starter de hoy)

## Idea central

> No mandes la orden de golpe: repártela. TWAP reparte en el tiempo; VWAP reparte donde hay volumen.
