# Lesson 7 · El mercado cambia. Tu motor sigue.

## Qué vas a construir

La entrada de datos de un futuro **backtesting engine**: convertir un JSON externo en
libros con los que preguntar `mid`, `spread`, `depth`, `imbalance` y `microprice`.
Primero comprobarás una fila pequeña; después usarás **24 fotos reales** del libro
BTC/USDT de Binance del **24/01/2022**. Un snapshot describe liquidez disponible;
no es una ejecución ni permite conocer lo ocurrido entre fotos.

## Archivos y ejecución

Todo lo necesario ya está en esta carpeta. No copies clases de otras lessons.

| Archivo | Responsabilidad |
| --- | --- |
| `base_book.py` | Level y OrderBook completos, proporcionados. No los modifiques. |
| `adapters.py` | Convertir parejas y adaptar el vocabulario externo. |
| `book.py` | Completar SnapshotBook, su factory y sus consultas. |
| `main.py` | Conectar y comprobar tus piezas; no definir clases. |
| `lob_data.py`, `data/` | Lector y NDJSON real proporcionados. |
| `opcionales.py` | Variantes 6A–6D, voluntarias. |
| `solutions/solucion.md` | Archivos completos, con los mismos encargos comentados y sus respuestas. |

Abre `enunciado.md` y los `.py`. Cada `TODO · Ejercicio 1A` coincide con un apartado.
Reemplaza `pass` o las asignaciones `None`; conserva los comentarios del encargo.
Desde `exercises`, ejecuta `python main.py`: al principio verás las 24 fotos leídas
y la invitación a completar 1A. Los huecos posteriores no bloquean ese primer paso.
Para probar hasta un punto: `python main.py --through 2B`.
Predice antes de ejecutar; guarda tu intento antes de consultar la solución.
Los resultados de los controles ya están escritos: tu trabajo es construir lo que consultan.

**LIVE:** 1–2, unos 20 min. **REQUIRED:** 3–5, unos 57 min incluidos estudio y controles.
**OPTIONAL:** 6, unos 13 min. Precios en USDT/BTC; tamaños y profundidad en BTC.

## Ejercicio 1 · Admitir y separar niveles

### 1A · Un nivel admite una pareja

En `adapters.py`, completa `level_from_values(price, size)`. Si falta cualquiera (`None`), devuelve `None`. Convierte size a float y omite tamaños no positivos; solo entonces convierte price y construye `Level`. Texto numérico es válido; texto no convertible debe producir ValueError. No cambies los argumentos. **Control:** `Level(98.0, 2.0)` para `'98','2'`; `None` para tamaño cero. Un Level reúne precio y cantidad, no una orden individual.

### 1B · Separa lados sin perder parejas

Completa `levels_from_snapshot(row, depth)`. Recorre sufijos 1…depth y los lados bid/ask; recupera price y size con `row.get`, llama a 1A y añade solo los Level admitidos a su lista. Devuelve `(bids, asks)`; no ordenes aún ni modifiques row. Usa la fila de `main.py`. **Predice:** ¿qué ask desaparece? **Control:** bids `[(98,2),(99,3)]`, asks `[(101,1)]`; el ask 103×0 se omite.

## Ejercicio 2 · Construir un libro y consultarlo

### 2A · Construye y ordena una vez

En `main.py`, sustituye `preview = None` por un OrderBook que reciba bids y asks. Su constructor está incluido. **Control:** bids `[(99,3),(98,2)]`; asks `[(101,1)]`. Explica por qué índice 0 representa el mejor nivel de cada lado y por qué ordenar precios por separado perdería las parejas.

### 2B · Pregunta al objeto

En `main.py`, guarda `mid0 = preview.mid` y `spread0` como mejor ask menos mejor bid. Lee los Level de preview; no vuelvas a row. **Control:** mid 100, spread 2 USDT/BTC. Mid es el centro de las cotizaciones; no afirma que puedas ejecutar allí.

## Ejercicio 3 · La factory de SnapshotBook · REQUIRED

### 3A · Una entrada alternativa al mismo libro

En `book.py`, completa `SnapshotBook.from_snapshot(cls, symbol, row, depth=10)` bajo `@classmethod`. Reutiliza 1B y devuelve `cls(symbol, bids, asks)`. El constructor proporcionado conserva symbol y llama al padre para ordenar. **Control:** `SnapshotBook`, `BTCUSDT`, mid 100. Explica por qué cls construye la clase receptora (incluida una posible hija), mientras self sería una instancia ya creada.

## Ejercicio 4 · Consultas reutilizables · REQUIRED

### 4A · Profundidad elegida

Completa `depth(side, levels=10)` en `book.py`. buy selecciona bids; sell selecciona asks. Devuelve suma de size de los primeros levels; otro side produce ValueError. **Control:** buy a 2 niveles = 5; sell = 1; sin niveles = 0. No modifiques ni consumas liquidez.

### 4B · Compón, no repitas la extracción

Completa `imbalance(levels=1)` llamando a depth para ambos lados. Devuelve `(bid-ask)/(bid+ask)`; total cero → None. **Control:** a 1 nivel, 0.5; dos listas vacías, None. Es una medida sin unidad del tamaño visible.

### 4C · Microprice y pesos cruzados

Completa la propiedad `microprice`. Un lado vacío o suma de tamaños cero devuelve None. Usa solo el mejor nivel de cada lado: `(bid.price*ask.size + ask.price*bid.size)/(bid.size+ask.size)`. **Control:** 100.5 USDT/BTC. Explica por qué más cantidad bid lo acerca al ask; no lo interpretes como precio futuro demostrado.

### 4D · La profundidad cambia la medida

En `main.py`, guarda im1 = imbalance(1), im2 = imbalance(2) y direction_changed según si su producto es negativo. **Control:** 0.5, 0.6667 al mostrar cuatro decimales, False. Explica que cambió la intensidad, no el signo.

### 4E · Compara dos referencias

En `main.py`, guarda tilt como microprice menos mid. **Control:** +0.5 USDT/BTC. Explica hacia qué lado se inclina en esta fila y por qué esto no es todavía una señal validada.

### 4F · Un control independiente

En `main.py`, calcula manual sumando directamente los size de los dos primeros bids, y d2 consultando depth buy a 2 niveles. **Control:** 5 y 5. Una cuenta independiente detecta un error que repetir dos veces el mismo método podría ocultar.

## Ejercicio 5 · La frontera del día real · REQUIRED

### 5A · Del JSON real a 24 objetos

Completa `snapshot_to_row(raw)` en `adapters.py`: copia timestamp y recorre las listas bid y ask. Cada elemento `price/volume` debe producir `bid_price_1/bid_size_1`, etc., numerados desde 1. Conserva decimales, todos los niveles y el raw original. En `main.py`, construye rows a partir de raw_snapshots, session_books usando tu factory con depth=10, y first_mid desde el primer libro. **Control:** 24 libros; first_mid = 36246.474609375. Abre `data/` para identificar los campos que adaptaste. El archivo es un extracto publicado, no una respuesta original de Binance. Muchas APIs entregan JSON; aquí leemos JSON guardado para reproducir la misma práctica.

### 5B · El motor consulta sin conocer volume

En `main.py`, recorre session_books, omite mids None y conserva el máximo en high, inicialmente None. **Control:** high = 37222.98046875 USDT/BTC; compara con los 24 mids observados. Explica por qué este consumidor no necesita conocer el campo volume ni los nombres de las columnas.

### 5C · La frontera que protege el sistema

No hay código por completar: lee el contraste ya incluido al final de `main.py`. Predice el efecto de duplicar todos los tamaños del banco de pruebas sin cambiar precios: depth buy a 2 niveles, imbalance(1), mid y microprice. Después ejecuta y explica qué magnitudes dependen de escala absoluta o de proporciones. Si otro proveedor llama qty a volume pero conserva unidades y significado, ¿qué función adaptarías? Si cambia las unidades, ¿qué normalización adicional necesitarías?

## Ejercicio 6 · Variantes independientes · OPTIONAL

### 6A · Columna ausente

En `opcionales.py`, copia row, borra bid_size_2 de la copia y construye changed con depth=2. **Control:** mejor bid 98 y original intacto. Reutiliza la misma factory.

### 6B · Cantidad cero

En `opcionales.py`, copia row, asigna '0' a bid_size_2 y construye zero_book. **Control:** mejor bid 98 y un solo bid; original intacto. Compara con ausencia y explica la misma regla de admisión.

### 6C · Spread medio del día

En `opcionales.py`, las filas reales ya están proporcionadas mediante tu adaptador. Consulta el spread de cada libro y guarda avg_spread = suma / cantidad. **Control:** compara con la resta independiente ask[0].price − bid[0].price de cada raw; ambos deben coincidir. La media es 0.4736328125 USDT/BTC.

### 6D · Una proporción con denominador

En `opcionales.py`, books ya está construido. Para cada pareja consecutiva, cuenta n_pairs, up_total, positive_cases (imbalance previo > 0) y up_after_positive. Un mid plano no sube. Calcula hit_rate = aciertos/casos positivos y base_rate = todas las subidas/n_pairs. **Control:** 23 parejas, 13 casos positivos, 8 aciertos condicionados y 12 subidas totales. La última foto carece de sucesora. Es una descripción de un único día horario; no mide rentabilidad ni demuestra predicción.

## Procedencia y alcance

Henker et al. (2024), DOI 10.5281/zenodo.10600374, CC BY 4.0.
24 snapshots horarios, 20 niveles por lado. La zona horaria no está indicada.
NDJSON = un objeto JSON por línea; se lee localmente, sin llamada de red.
El dibujo muestra cinco niveles; tus libros usan diez. No interpolamos entre fotos.
Más información y licencia en `data/README.md`. L8 trabajará con este contrato de libro
para planificar, validar y aplicar fills; hoy solo construyes y consultas estado.
