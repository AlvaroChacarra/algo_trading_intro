# Banco sintético de L8

`btc_lob_snapshots.csv` es el fixture docente de 500 snapshots BTCUSDT que
consumen L8–L14. No procede de un exchange ni representa operaciones reales.
Cada fila contiene diez niveles por lado: `bid_price_N`, `bid_size_N`,
`ask_price_N`, `ask_size_N`, y un timestamp docente. CSV devuelve texto.
Precios: USDT/BTC. Tamaños: BTC. `SnapshotBook.from_snapshot` adapta la fila.

En 6A y 7D usamos solo la primera fila. El libro pequeño de 1A–6B es otro
control sintético: USD/BTC y cantidades BTC. El histórico real JSON de L7
es un dato diferente; no se necesita trasladarlo para comenzar esta práctica.
Aquí no avanzamos el tiempo ni modelamos prioridad de órdenes individuales.
El remanente LIMIT descansa en la foto actual; L9 reemplaza esa foto al avanzar.
