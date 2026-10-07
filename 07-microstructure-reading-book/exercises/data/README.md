# El día real de L7 · Binance BTC/USDT · 24/01/2022

El fichero `binance-btcusdt-2022-01-24.ndjson` contiene 24 snapshots L2
históricos, de 00:00 a 23:00, con 20 niveles agregados por lado. Hay una foto
por hora: entre dos fotos no conocemos los eventos, las órdenes individuales
ni las ejecuciones. Un snapshot es estado disponible, no volumen negociado.

Fuente: Robert Henker, Daniel Atzberger, Jan Ole Vollmer, Willy Scheibel,
Jürgen Döllner y Markus Bick (2024), *Order Book Data from Six Crypto-Exchanges*.
[Zenodo · DOI 10.5281/zenodo.10600374](https://doi.org/10.5281/zenodo.10600374).
Licencia [Creative Commons Attribution 4.0](https://creativecommons.org/licenses/by/4.0/).

Se seleccionaron las 24 líneas de ese día de
`Binance-BTC-USDT-20220101-000000.ndjson`, dentro de `order-book-data.zip`.
Las líneas se conservan byte por byte: no se modificaron precios, cantidades,
orden ni precisión. Esta selección es la única modificación del archivo publicado.
El ZIP original tiene MD5 `f1c7535f1287e4baccd2e8d2761610b1`;
este extracto, SHA-256 `11bcb6dae72f32e67ebd2b69f17da3fb239bb51abc2cd35115f39c4b08ffab7d`.

## Formato crudo del archivo publicado

NDJSON significa un objeto JSON por línea. `timestamp` es una fecha y hora
en texto; la fuente no indica zona horaria, por lo que no le asignamos UTC.
`bid` y `ask` son listas de niveles. Cada nivel tiene `price` en USDT por BTC
y `volume` en BTC. Los decimales y su precisión son los del archivo publicado;
la presentación solo redondea al mostrar. No es la respuesta original de la API
del exchange ni un feed de eventos sin muestreo.

`lob_data.py` solo abre y deserializa el JSON. En L07-B08 tú construyes
`snapshot_to_row`: `volume` pasa a llamarse `size`, y el índice se convierte
en un sufijo desde 1. Después tu factory convierte y filtra parejas, crea
`Level`, ordena el libro y permite consultar métricas. Se conservan 20 niveles
en las filas; la factory usa los primeros 10 y la presentación dibuja 5.
No se rellenan huecos ni se interpolan libros entre horas.

La fila de precios 98/99/101 del inicio es un ejemplo controlado, separado
del histórico: permite ensayar texto, ausencia, cero y desorden. L8 y L9
reutilizan la interfaz de tu factory con otros ejemplos controlados; no
presuponen continuidad temporal con este día de Binance.
