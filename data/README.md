# data/ — dataset del libro de órdenes

`btc_lob_snapshots.csv` — **500 snapshots** de un libro de órdenes limit, introducidos
como frontera de datos externos en L7, que
imita a BTCUSDT: 10 niveles por lado (precio y tamaño), a cadencia de 60 s.

## Provenance

Es un dataset **sintético**, generado para el curso, no datos reales de un
exchange. El mid sigue un paseo aleatorio en torno a ~100 000 y cada nivel se
rellena con profundidad y tamaños plausibles. Se generó una vez y se versiona
tal cual: así **todo el curso es reproducible y funciona sin conexión**, y los
números que aparecen en los documentos (que se calculan corriendo el motor sobre
estos snapshots en tiempo de compilación) son estables.

Todo snapshot y volumen del CSV es, por tanto, **sintético**. Los `Fill` que
aparecen en las lecciones son **simulados** por la implementación canónica al
ejecutarse contra ese replay; tampoco representan operaciones observadas en un
exchange.

Al ser sintético, no hay estructura oculta que explotar: la actividad del libro
es esencialmente estacionaria (esto se usa a propósito en L12 para enseñar
cuándo NO merece la pena añadir un modelo predictivo).

## Quién lo usa

- `framework/exchange/_data/btc_lob_snapshots.csv` es la **copia canónica** que
  carga el motor (`Market.sample()` / `Market.from_csv()`). Este archivo de
  `data/` es una copia idéntica para inspección y para `smoke_test.py`.
- Lo consumen por primera vez los ejercicios de lectura de L7; después, el loop de
  simulación (L9+), el framework de backtesting (L10+) y
  las estrategias de ejecución (L12).

## Formato

```
timestamp, bid_price_1, bid_size_1, …, bid_price_10, bid_size_10,
           ask_price_1, ask_size_1, …, ask_price_10, ask_size_10
```
Los niveles vienen ordenados de mejor a peor (bid_1 = mejor bid, ask_1 = mejor ask).
