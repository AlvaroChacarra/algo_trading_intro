# L6 · Cambia la señal. Conserva el motor.

El mismo mercado, dos respuestas: **RSI dice vender; imbalance dice comprar**.
¿Cómo conectamos reglas tan distintas sin escribir un programa para cada una?
Construyes dos hijas de `Signal`; ambas reciben `data` y devuelven `buy/sell/hold`.
El libro y el indicador ya están incluidos. Una decisión es texto: no envía órdenes ni crea fills.

## Antes de empezar

| Archivo | Procedencia y responsabilidad |
| --- | --- |
| `book.py` | Heredado de L5: `Level(price, size)` y `OrderBook(bids, asks)`. No reescribas la fórmula. |
| `indicators.py` | Proporcionado: `rsi(closes, period=14)`. Lo consumes; no construyes el indicador. |
| `signals.py` | Construyes herencia, inicialización común y decisiones. Imports, firmas, validación de parámetros y llamada al indicador proporcionados. |
| `main.py` | Conectas las piezas; datos, consultas iniciales, casos límite y guarda de ejecución proporcionados. |
| `opcionales.md` | Seis variantes OPTIONAL independientes. No hacen falta para cerrar el principal. |
| `solutions/solucion.md` | Consulta después del intento; archivos REQUIRED completos y respuestas opcionales. |

Desde `06-oop-iii-inheritance/exercises`, abre terminal y ejecuta `python main.py`.
Al principio verás `dato compartido | RSI 14: 70.0 | imbalance: None` y
`base instanciada: falta el decorador`. Es el estado incompleto previsto.
Los huecos posteriores no bloquean el primer resultado.

**Conserva tu trabajo:** guarda una copia personal de esta carpeta y trabaja dentro
 de ella. Todos los módulos necesarios están incluidos; `book.py` es una base resuelta
 y no se edita. Cada ejecución crea objetos nuevos.

**Autonomía:** consultas a objetos, listas y bucles se aplican con menos ayuda.
La herencia, el contrato abstracto y `super()` reciben guía. Escribirás la interpretación
 del RSI a partir de las reglas, sin reconstruir el indicador.
**Datos y contrato:** son ejemplos sintéticos docentes, escritos en `main.py`.
`data = {'closes': closes, 'imbalance': imb}` es el mismo diccionario para ambas reglas.
`closes` contiene cierres diarios en USD, de antiguo a reciente, todos finitos;
15 cierres permiten medir 14 cambios. No son un flujo ni datos en tiempo real.
El libro tiene bid 99 USD × 3 unidades y ask 101 USD × 1.
`imbalance(levels=1)` devuelve un número sin unidades entre −1 y 1; cero tamaño
total devuelve `None`, no cero. Un único lado con tamaño positivo devuelve ±1.
Una hija consulta `closes`; la otra consulta `imbalance`. Ninguna recibe la otra señal.

**RSI proporcionado:** suma las subidas y las bajadas de los últimos `period` cambios,
calcula sus medias aritméticas y compara su fuerza. El resultado está entre 0 y 100:
cuanta más subida relativa, mayor RSI. Usamos una **ventana simple**, sin suavizado de
Wilder. `rsi(closes, 14)` devuelve `70.0` en el ejemplo: 7 USD de subidas y 3 de bajadas.
Sin `period + 1` cierres devuelve `None`; solo subidas → 100, solo bajadas → 0,
ventana plana → 50. La regla interpretará RSI bajo como compra y RSI alto como venta;
el indicador por sí solo no da una orden ni demuestra que esa regla sea rentable.

**Ruta:** ejercicios 1–6, unos 20 min LIVE en total, integración incluida. La consolidación
REQUIRED conserva 22 min de lectura: super 6, contrato ABC 8 y quiz 8. La lectura
7 acompaña los 6 min de super ya previstos. Revisa también las escenas ABC y quiz.
Opcionales: 16 min estimados si haces los seis. Estos tiempos no se han medido con alumnos.

## Ejercicio 1 · Dos medidas, el mismo dato — LIVE · 3 min

### 1A · Consulta el libro incluido
En `main.py`, sustituye el valor inicial de `imb` por la consulta al libro con un
nivel. No copies clases ni calcules la fórmula aquí. Antes de ejecutar, predice el
signo y valor con tamaños 3 y 1. El diccionario ya está proporcionado: llevará la medida
que acabas de obtener. Guarda y ejecuta aunque las reglas sigan incompletas.

<details><summary>Contrasta después de predecir</summary>

`dato compartido | RSI 14: 70.0 | imbalance: 0.5`. La consulta del libro produce
(3−1)/(3+1)=0.5; el helper calcula el RSI sobre los cierres.

</details>

## Ejercicio 2 · Declara el contrato — LIVE · 3 min

### 2A · Impide crear una regla sin decisión
En `signals.py`, añade `@abstractmethod` encima de `Signal.decide`.
`Signal(ABC)` hereda el mecanismo de clases abstractas del módulo estándar `abc`.
El decorador exige que una hija concreta sobrescriba `decide`.
`raise NotImplementedError` por sí solo no impide construir la base; el decorador sí.

El constructor proporcionado guarda `self.name`: cualquier regla de esta familia
puede identificarse. La base fija la llamada `decide(self, data: dict) -> str`;
**cada hija elige su respuesta**. Las anotaciones documentan entrada y retorno;
ABC no valida los campos del diccionario ni la calidad económica de la regla.
Ejecuta `main.py`: el `try/except TypeError` proporcionado muestra que la base
no se puede crear. No captures errores de todo el programa.

## Ejercicio 3 · Una hija que lee el RSI — LIVE · 4 min

### 3A · Declara la herencia e inicializa el nombre
En `signals.py`, cambia la cabecera de `RSISignal` para que herede de `Signal`.
La notación es `class RSISignal(Signal):`: esta regla **es una** señal de esa familia.
Dentro de su constructor completa la inicialización común con
`super().__init__('RSI')`. Ejecuta el constructor del padre sobre **este mismo objeto**,
y guarda `name`; la hija añade después sus parámetros. Si sobrescribes `__init__`,
Python no llama automáticamente al constructor del padre.

`period`, `buy_level` y `sell_level` ya se guardan. La validación proporcionada exige
periodo entero positivo y `0 <= buy_level < sell_level <= 100`.
Comprueba el nombre sin completar aún el consumidor:
`python -c "from signals import RSISignal; print(RSISignal().name)"` muestra `RSI`.

### 3B · Escribe tu implementación de decide
En `signals.py`, completa el cuerpo de `RSISignal.decide` después de la llamada
proporcionada a `rsi`. `value` es un número entre 0 y 100 o `None`; la ausencia ya
se trata devolviendo `'hold'`.

Escribe las condiciones y sus retornos usando los atributos de la instancia:

| Condición | Respuesta |
| --- | --- |
| `value <= self.buy_level` | `'buy'` |
| `value >= self.sell_level` | `'sell'` |
| Interior de la banda | `'hold'` |

Esta implementación **sobrescribe / override** el método del padre. No añadas
`@abstractmethod` en la hija: queremos poder crearla. No fijes 30/70 en las condiciones;
los niveles son parámetros. Con `[100] * 15`, la ventana plana produce RSI 50:
`python -c "from signals import RSISignal; print(RSISignal().decide({'closes': [100]*15}))"`
debe mostrar `hold` con la configuración inicial.

### 3C · Sigue una llamada real
En `main.py`, crea `rsi_rule = RSISignal()` y muestra su nombre y decisión con
`print(rsi_rule.name + ':', rsi_rule.decide(data))`.
Python pasa `rsi_rule` como `self` y el diccionario como `data`. No pases `self` tú.
Predice antes de ejecutar: ¿compraría o vendería con RSI exactamente 70?
`python main.py` añade `RSI: sell` a las dos líneas que ya funcionaban.

## Ejercicio 4 · Otra hija, otra regla — LIVE · 4 min

### 4A · Conserva el estado común y trata la ausencia
En el constructor de `ImbalanceSignal`, inicializa el nombre con
`super().__init__('Imbalance')`. La validación y `self.threshold` están proporcionados;
la banda requiere un umbral entre 0 y 1. No vuelvas a guardar `self.name` en cada hija.
En `decide`, `data.get('imbalance')` ya extrae la medida: si es `None`, devuelve
`'hold'` antes de comparar. Una medida ausente no justifica operar.

### 4B · Construye una banda simétrica
Por encima de `self.threshold` devuelve `'buy'`; por debajo de su negativo devuelve
`'sell'`; en el resto devuelve `'hold'`. Usa `>` y `<` estrictos: igualar el umbral
no lo supera. **Esta frontera difiere del RSI**, cuyos niveles sí activan la decisión.
Usa el atributo de la instancia, no escribas 0.3 dentro de las condiciones.

### 4C · Conecta la segunda regla
En `main.py`, crea `imbalance_rule = ImbalanceSignal(0.3)` y muestra su nombre y
su decisión sobre **el mismo `data`**. Predice y contrasta: mientras RSI vende,
imbalance compra. Ambas son `Signal`, aunque responden de manera distinta.

## Ejercicio 5 · Cambia la regla, conserva el bucle — LIVE · 3 min

### 5A · Una llamada para dos hijas
En `main.py`, crea `rules` con `rsi_rule` e `imbalance_rule`. Recorre la lista,
llama a `rule.decide(data)` y acumula las respuestas en `decisions`; imprímelas.
Listas, bucles y `append` ya los conoces: monta esto sin preguntar por el nombre
de la clase. Cambia el objeto receptor; el código que llama queda igual.

<details><summary>Contrasta después de predecir</summary>

`mismo dato, dos reglas: ['sell', 'buy']`. Es polimorfismo: misma interfaz,
implementaciones distintas. No son dos órdenes y el padre no elige por sus hijas.

</details>

## Ejercicio 6 · Fronteras y parámetros — LIVE · 3 min

### 6A · Predice antes de consultar
En `main.py`, `rsi_inputs` ya contiene cuatro diccionarios: cierres que dan RSI 30,
RSI 70, historia insuficiente y ventana plana. Muestra
`[rsi_rule.decide(item) for item in rsi_inputs]`. Haz lo mismo con `imbalance_inputs`
usando `imbalance_rule`; contiene ausencia y ambos umbrales exactos.

Después muestra tres decisiones sobre el `data` original: `RSISignal(period=3)`,
`RSISignal(buy_level=20, sell_level=80)` e `ImbalanceSignal(0.6)`.
¿Por qué cambiar el período y cambiar los niveles son cambios diferentes?
No reescribas el indicador ni las condiciones; crea instancias con otros parámetros.

### 6B · Cambia el mercado, conserva el llamador
Sin mirar la solución: crea otro libro con los mismos precios y tamaños 1 y 3.
Construye `other_data` con `closes30` proporcionado y su imbalance. Predice las dos
respuestas y aplícales el mismo bucle o comprensión sobre `rules`, sin tocar
`signals.py`. Explica qué campo lee cada hija y qué conservarías al añadir una tercera.
Esta variación comprueba la conexión dato → regla; no prueba rentabilidad.

## Ejercicio 7 · Heredar inicialización — REQUIRED · lectura ya incluida

### 7A · Traza el mismo objeto
En la presentación y en 3A ya usaste `super` para inicializar `name`. Esta base concreta distinta
permite aislar qué ocurre al escribir otro constructor. Lee la escena `super` y
contrasta el bloque en una terminal Python si lo necesitas; no cambia `signals.py`.

```python
class Strategy:
    def __init__(self, name):
        self.name = name
    def decide(self, data):
        return 'hold'

class SinInit(Strategy):
    pass

class SinSuper(Strategy):
    def __init__(self, name, threshold):
        self.threshold = threshold

class ConSuper(Strategy):
    def __init__(self, name, threshold):
        super().__init__(name)
        self.threshold = threshold
```

Predice los atributos de `SinInit('a')`, `SinSuper('b', 0.3)` y `ConSuper('c', 0.3)`;
contrasta con `vars(objeto)`. Sin constructor propio se hereda el de la base. Al
escribir uno propio lo sustituyes: el anterior no se ejecuta automáticamente.
`super().__init__(name)` llama al constructor heredado sobre el mismo `self`;
no crea otro objeto. Después la hija añade su atributo. Las tres heredan `decide`.
¿Qué ocurriría al consultar `.name` en el segundo objeto? Respuesta en la solución.

## Ejercicio 8 · Variantes OPTIONAL

No son requisito para L7 ni para resolver 1–7. Abre `opcionales.md`; cada apartado
incluye arranque independiente, punto de edición y comprobación.

### 8A · Cambia solo los niveles de RSI
`opcionales.md`, Variante 8A · 2 min.
### 8B · Dos reglas ante otro dato
`opcionales.md`, Variante 8B · 2 min.
### 8C · Conserva el estado de la base
`opcionales.md`, Variante 8C · 3 min.
### 8D · El cuerpo no quita la abstracción
`opcionales.md`, Variante 8D · 3 min.
### 8E · Método disponible y familia
`opcionales.md`, Variante 8E · 2 min.
### 8F · Dos reglas, una llamada
`opcionales.md`, Variante 8F · 4 min.

## Cierre

Puedes explicar la herencia `Signal → RSISignal / ImbalanceSignal`, el estado común
`name`, quién recibe cada llamada y por qué la base no se instancia. Distingues las
fronteras inclusivas del RSI de la banda estricta del imbalance; cambias parámetros
sin cambiar el llamador. `python main.py` reproduce el recorrido;
`python -c "import main"` no imprime nada. Conserva el intento antes de consultar.
L7 reutiliza el libro de L5 para estudiar snapshots; no importa estas señales.
L10 retoma el patrón con otra API: recibe un libro y devuelve órdenes, no etiquetas.
