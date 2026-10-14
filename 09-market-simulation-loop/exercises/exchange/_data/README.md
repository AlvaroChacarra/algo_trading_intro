# Datos del replay de L9

`btc_lob_snapshots.csv` es el fixture docente sintético de 500 snapshots BTCUSDT
que consumen L8–L14. No procede de un exchange ni representa operaciones reales.
Cada fila contiene diez niveles por lado: `bid_price_N`, `bid_size_N`,
`ask_price_N`, `ask_size_N`; N va de 1 a 10. `timestamp` es un instante docente
en segundos Unix. Precios: USDT/BTC. Tamaños: BTC. CSV entrega valores de texto;
la factory incluida `SnapshotBook.from_snapshot` los adapta y descarta tamaños
no positivos o niveles incompletos.

En 4A recorres las 500 filas en el orden proporcionado y compras una unidad en
el índice 9, después del décimo step. Usa symbol="BTCUSDT". La cuenta comienza
con 1000 USDT y posición 0; no hay comisiones ni límite de financiación, por lo que
puede quedar caja negativa. En 5C el calendario OPTIONAL solicita 0.1 BTC cada 50 fotos
hasta confirmar 1 BTC; esa extensión no hace falta para continuar.

`scenarios.py` incluye un control distinto con dos fotos: precios USD/BTC,
tamaños BTC y timestamp 0/1 como orden didáctico. Esas fotos permiten predecir
caja 899 / posición 1 tras comprar a 101, y equity 1001 al pasar al mid 102.
El histórico real JSON de L7 es otro dato; no hay que trasladarlo.

ReplayMarket entrega una fila por step. El matching consume la foto activa;
el step siguiente sustituye el libro desde el histórico. Una LIMIT pendiente
no se conserva entre fotos y desconocemos los eventos intermedios. La cartera
externa conserva únicamente los fills que el experimento ha registrado.
Estos datos sirven para estudiar coordinación y contabilidad, no para atribuir
rentabilidad real a una señal.
