# Clase 12 — VWAP — Ejecución

> Repartir una orden grande en trozos, comparar ejecución inmediata, TWAP y VWAP, y construir un perfil estático honesto. La predicción dinámica de volumen queda como extensión OPTIONAL y no es prerrequisito posterior.

## Contexto teórico

Primer algoritmo de **ejecución**. Mandar una orden grande de golpe barre el libro y paga
impacto; **trocearla** en el tiempo lo reduce. Dos baselines:
- **TWAP** (time-weighted): trozos iguales en el tiempo. Honesto y difícil de batir sin info.
- **VWAP** (volume-weighted): pondera por el **perfil de volumen** intradía, para acercarse al
  precio medio ponderado por volumen — el benchmark estándar de ejecución institucional.

El perfil son pesos relativos: se normalizan, así que importan las proporciones, no la escala.

## Qué construyes hoy

**VWAPStrategy: slicing, TWAP y perfil de volumen estático**

`exchange/strategies/vwap.py` (`VWAPStrategy(symbol, side, total_size, horizon, profile)`):
en cada tick emite una market order del tamaño del trozo (peso normalizado × total). Sin
perfil → TWAP uniforme. Es una subclase de `Strategy`: se enchufa al `Backtest` exactamente
igual que cualquier otra — primera demostración del valor del framework de L10.

La predicción dinámica de volumen queda como profundización **OPTIONAL**: ningún contenido ni
assessment posterior la presupone; LIVE + REQUIRED se sostienen con slicing, TWAP, el perfil
VWAP estático y una comparación empírica honesta.

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

- `presentation/` — documento interactivo (o deck) + guion del profesor
- `exercises/12_build_exercises.ipynb` — construyes la pieza (rutas LIVE / REQUIRED / OPTIONAL declaradas)
- `exercises/12_auxiliary.ipynb` — el gimnasio: drills + profundización opcional
- `exercises/exchange/` — el paquete que vienes construyendo (starter de hoy)

## Idea central

> No mandes la orden de golpe: repártela. TWAP reparte en el tiempo; VWAP, según un perfil de volumen. Un modelo solo merece quedarse si los datos demuestran que mejora el baseline.
