# Datos de L11

La práctica y el laboratorio principal usan las cinco fotos sintéticas de
`metrics_support.py`: mids 100, 102, 100, 103, 97 USDT/BTC; tamaños en BTC.
La foto inicial tiene bid 99×2 y asks 101×0.4/102×0.6. Una compra de 1 BTC
confirma dos fills. Timestamps 0/1 explícitos; el resto usa el índice de replay
2/3/4. Son índices docentes, no fechas. Campos ausentes se omiten.

Caja inicial 1000 USDT, posición cero, fee_bps 0 o 10 declarado por experimento.
Una comisión de 10 bps es 0.1% del nominal confirmado; no se incluye dentro del
coste de precio. Sin restricciones de financiación, margen ni inventario.
ResearchBacktest acepta NewOrder MARKET/IOC, sin cola pasiva entre fotos.
El mid anterior al matching permite valorar aunque se agote un lado del libro.

El CSV `btc_lob_snapshots.csv` proporciona 500 fotos sintéticas de BTCUSDT,
diez niveles por lado. Timestamp en segundos Unix; bid_price_i/ask_price_i
USDT/BTC y bid_size_i/ask_size_i BTC. DictReader devuelve texto, adaptado por
la factory local. Se usa en la ampliación de Estudio, con el mismo runner y caja;
no hay descarga ni API durante la práctica. El SDK puede consultarlo con
Market.sample(), pero su Backtest no sustituye ResearchBacktest.

Las curvas de PnL de la apertura son series ilustrativas, no backtests de
estrategias: max_drawdown las mide con initial_equity=0. El control aleatorio
proporcionado RandomControl opera con probabilidad 0.6, clip 0.05 y semillas
7/21/99; actividad y exposición pueden diferir de la señal. Ningún rango de
esas tres semillas demuestra alpha. El JSON histórico real de L7 es otra fuente.
Datos generados para el curso, redistribuibles con los ejercicios.
