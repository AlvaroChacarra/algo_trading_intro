# Datos de L10

La práctica y la presentación usan las dos fotos **sintéticas** de `scenarios.py`.
No hay una API ni una descarga durante el ejercicio. Símbolo BTC, precios USDT/BTC,
tamaños BTC; timestamps 0 y 1 indican el orden del ejemplo, no una fecha real.
Foto 0: bid 99×2, asks 101×0.4 y 102×0.6; mid 100.
Foto 1: bid 101×2, ask 103×1; mid 102. Los niveles ausentes se omiten, no se rellenan.
Una compra MARKET de 1 BTC produce dos fills en la primera foto y puede agotar el ask.
El runner conserva el mid **previo** al matching para valorar esa foto.

Caja inicial 1000 USDT; posición inicial cero. La comisión se expresa en bps:
1 bps=1/10000 del importe confirmado. Sin límite de financiación, margen ni riesgo;
la variante SellOnce permite posición negativa. Son controles docentes, no evidencia
sobre rentabilidad. Se acepta NewOrder MARKET/IOC; no Cancel/LIMIT/FOK en este runner.
El libro se sustituye al avanzar, sin cola pasiva ni ejecución entre fotos.

El CSV incluido `btc_lob_snapshots.csv` es el fixture sintético de consulta del SDK:
500 fotos BTCUSDT, diez niveles por lado, timestamps en segundos Unix,
`bid_price_i`/`ask_price_i` en USDT/BTC y `bid_size_i`/`ask_size_i` en BTC.
DictReader devuelve texto; la factory incluida lo adapta. Los módulos de referencia
pueden consultarlo mediante Market.sample(); no se necesita para completar la práctica.
Es una fuente distinta del JSON histórico real de L7. Generación determinista en la
fuente privada del curso; puede redistribuirse con los ejercicios.
