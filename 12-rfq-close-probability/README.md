# L12 — RFQ & Probabilidad de Cierre

## Misión
Dado un RFQ de renta fija, **¿cuánto spread debemos cotizar para maximizar el ingreso esperado?**

La respuesta requiere modelar `P(cierre | spread)` — una curva logística diferente para cada tipo de cliente — y luego optimizar `E[Rev] = P(s) × s × Q`.

## Tres ideas clave

| Idea | Concepto |
|------|----------|
| Filtrar antes de modelar | Los 243 RFQs ambiguos (`won=0, closed_away=0`) contaminan la variable objetivo. Solo usamos los 557 con resultado conocido. |
| Logística por tier | P(cierre\|s) es una sigmoide decreciente en el spread. Tier 3 tiene β₁ > 0 — caso especial, modelo oportunista. |
| Q no mueve s* | El spread óptimo s* = −1/(β₁·(1−p*)) no depende del nominal. Solo escala el ingreso esperado. |

## Dataset

800 RFQs sintéticos de bonos Tesoro español (ESP 2Y, 5Y, 10Y, 15Y, 30Y).
10 días de trading · 3 tiers de cliente · 19 columnas.

| Columna clave | Descripción |
|---------------|-------------|
| `tier` | Calidad del cliente (1=premium, 3=retail) |
| `spread_bp` | *(calculada)* Spread cotizado en puntos básicos: `(quoted_price - mid) / dv01` |
| `won` | 1 si el cliente aceptó nuestra cotización |
| `closed_away` | 1 si otro dealer ganó el RFQ |
| `cover_price` | Precio al que cerró el competidor (si disponible) |

## Flujo de clase

```
presentation/ (28 min)
  Hero: terminal RFQ con 3 destinos posibles
  B1:   filtrado de datos y la trampa de price discovery
  B2:   curvas logísticas por tier + slider de spread
  B3:   dual chart P(s) + E[Rev], slider Q, s* invariante
  
exercises/ (12 min en clase)
  E1–E3: cargar datos, spread_bp, filtrar df_model
  E4–E5: ajustar logística, predict_close_probability()
  E6–E7: expected_revenue(), optimal_spread() [si vamos bien]
  E8–E10: visualización, 2 features, RFQModel class [bonus]
```

## Continuidad con L13
`s*` calculado en este ejercicio asume que cotizamos el mismo spread siempre. En L13 veremos que **el inventario acumulado** debería desplazar ese spread en tiempo real — la idea central del modelo Avellaneda-Stoikov.
