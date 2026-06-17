# Clase 12 — VWAP — Ejecución

> Primer algoritmo de ejecución: repartir una orden grande en trozos a lo largo de la sesión. Empezamos con baselines (TWAP, VWAP) y subimos a predecir el volumen con el flujo reciente.

## Contexto teórico

Primer algoritmo de **ejecución**. Mandar una orden grande de golpe barre el libro y paga
impacto; **trocearla** en el tiempo lo reduce. Dos baselines:
- **TWAP** (time-weighted): trozos iguales en el tiempo. Honesto y difícil de batir sin info.
- **VWAP** (volume-weighted): pondera por el **perfil de volumen** intradía, para acercarse al
  precio medio ponderado por volumen — el benchmark estándar de ejecución institucional.

El perfil son pesos relativos: se normalizan, así que importan las proporciones, no la escala.

## Qué construyes hoy

**VWAPStrategy: repartir una orden por el perfil de volumen (estático y dinámico)**

`exchange/strategies/vwap.py` (`VWAPStrategy(symbol, side, total_size, horizon, profile)`):
en cada tick emite una market order del tamaño del trozo (peso normalizado × total). Sin
perfil → TWAP uniforme. Es una subclase de `Strategy`: se enchufa al `Backtest` exactamente
igual que cualquier otra — primera demostración del valor del framework de L8.

## Ejercicios de construcción

- **1. Schedule TWAP** — pesos uniformes
- **2. Lanza un VWAPStrategy** — estrategia de ejecución
- **3. Perfil VWAP a medida** — pasar un perfil
- **4. Precio medio de ejecución** — VWAP de tus fills
- **5. Media rolada** — ventana de los últimos k
- **6. Predice el próximo volumen** — usar la ventana
- **7. Perfil dinámico** — normalizar predicciones
- **8. Factor de corrección** — ir a tiempo

## Estructura de la carpeta

- `presentation/` — presentación interactiva + guion del profesor
- `exercises/12_build_exercises.ipynb` — construyes la pieza (núcleo 1-3, luego el resto)
- `exercises/12_auxiliary.ipynb` — profundización opcional
- `exercises/exchange/` — el paquete que vienes construyendo (starter de hoy)

## Idea central

> No mandes la orden de golpe: repártela. TWAP reparte en el tiempo; VWAP, donde hay volumen; y el flujo reciente afina el plan.
