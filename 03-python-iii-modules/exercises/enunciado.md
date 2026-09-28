# Lesson 3 · Módulos, imports y programa principal

## Objetivo

Reutilizar mediante imports una referencia equivalente de las consultas de L2:
`functional.py` construye órdenes y encuentra precios; `analytics.py` calcula medidas; `main.py` conecta las piezas.
Un módulo es un archivo Python del que puedes importar nombres. Al terminar,
podrás explicar de qué archivo viene cada función y cuándo se ejecuta el programa.

## Archivos

| Archivo | Tu trabajo |
| --- | --- |
| `functional.py` | Referencia proporcionada de las consultas de L2; léelo, no lo modifiques. |
| `analytics.py` | Completar `describe(orders)` (ejercicio 1). |
| `main.py` | Importar, conectar y probar las piezas (ejercicios 2–4). |
| `solutions/solucion.md` | Referencia textual por archivo y ejercicio. |

`functional.py` no importa tu respuesta personal de L2: proporciona consultas
equivalentes y añade en `make_order` la validación de lado, precio y tamaño que
usarás en L3. Aquí practicarás cómo reutilizar ese módulo desde otros archivos.

## Cómo trabajar

Abre estos archivos juntos en `exercises`. Sigue los ejercicios en orden: cada
apartado coincide con un comentario `TODO · Ejercicio N.a` en el archivo indicado.
El enunciado contiene el detalle; el TODO te sitúa donde debes escribir.
Guarda los cambios antes de ejecutar. Las plantillas están incompletas: el error
provisional de `describe` se retira en el ejercicio 1. Consulta la solución después
de intentar el ejercicio. La guarda final está proporcionada: consérvala para
ejecutar `python main.py` desde `exercises` después de cada apartado del ejercicio 2.
El ejercicio 5 es OPTIONAL y no hace falta para seguir.

## Ejercicio 1 · Completa `analytics.py`

La importación de `best_prices` ya está escrita. Esta función devuelve una pareja:
`bid` es la mejor compra y `ask` la mejor venta; un lado ausente vale `None`.

### 1.a · Reutiliza los precios

Dentro de `describe(orders)`, llama **una sola vez** a `best_prices(orders)` y guarda
sus dos resultados en `bid, ask`. No vuelvas a filtrar las órdenes: esa
responsabilidad pertenece a `functional.py` y ya se resolvió en L2.

### 1.b · Trata el lado ausente

Si `bid is None` o `ask is None`, devuelve `{"mid": None, "spread": None}`.
No uses cero para indicar ausencia: sería un precio y cambiaría el significado.
Esta salida debe ocurrir antes de intentar operaciones aritméticas.

### 1.c · Calcula las medidas

Si existen ambos lados, devuelve un diccionario con `mid = (bid + ask) / 2`
y `spread = ask - bid`. `mid` es el punto medio y `spread` la distancia entre
ambos precios. Sustituye el `raise NotImplementedError` provisional por tu código.
**Comprobación:** con compra 99 y venta 101 esperas mid 100.0 y spread 2;
con solo compras, ambos serán `None`. Los verás al ejecutar el ejercicio 2.

## Ejercicio 2 · Construye `main.py`

### 2.a · Importa las piezas

Fuera de `main()`, importa `make_order` desde `functional` y `describe` desde
`analytics` mediante `from ... import ...`. No copies funciones entre archivos.

### 2.b · Observa un mercado con ambos lados

Dentro de `main()`, crea una lista `orders` con `make_order("buy", 99, 2)` y
`make_order("sell", 101, 3)`. Los argumentos son lado, precio y tamaño.
Imprime `describe(orders)` precedido de `mercado:`. Antes de ejecutar, calcula
mentalmente el punto medio y la distancia entre los precios.

### 2.c · Observa un mercado incompleto

Crea `only_buys`, una lista con `make_order("buy", 99, 2)`, e imprime
`describe(only_buys)` precedido de `solo compras:`. Compruebas así que reutilizar
una función incluye respetar sus casos límite, no solo el caso cómodo.

**Salida de estas dos consultas**, usando la entrada ya proporcionada:

```text
mercado: {'mid': 100.0, 'spread': 2}
solo compras: {'mid': None, 'spread': None}
```

## Ejercicio 3 · Utiliza el error del módulo

### 3.a · Provoca una entrada inválida

Después de las consultas, dentro de `main()`, escribe un bloque `try` que intente
`make_order("buy", -10, 1)`. El precio negativo incumple la validación
proporcionada en `make_order`.
No cambies `make_order` para aceptar esta orden.

### 3.b · Captura el error concreto

Añade `except ValueError as error:` e imprime `orden rechazada:` junto con
`error`. Capturar solo `ValueError` permite tratar esta entrada esperada sin
ocultar otros errores de programación. Esperas `orden rechazada: price debe ser positivo`.

## Ejercicio 4 · Separa importar de ejecutar

### 4.a · Experimenta con la entrada proporcionada

La guarda final ya permitió probar cada paso. Ahora compara: sustituye temporalmente
las dos líneas por `main()` sin sangría. Predice qué ocurrirá al ejecutar
`python -c "import main"` y compruébalo: también se muestran las demostraciones.
Restaura después `if __name__ == "__main__":` y su llamada indentada a `main()`.
Así puedes importar definiciones sin ejecutar las pruebas.

### 4.b · Comprueba ambos usos

En una terminal situada en `exercises`, ejecuta por separado:

```bash
python main.py
python -c "import main"
```

El primero imprime los tres resultados anteriores; el segundo no imprime nada.
Si el segundo muestra resultados, revisa qué instrucciones quedaron fuera de
`main()` o de la guarda. Estos comandos se escriben en terminal, no en el archivo.

## Ejercicio 5 · OPTIONAL · Otra forma de importar

### 5.a · Haz explícito el módulo

En `main.py`, sustituye `from analytics import describe` por `import analytics`.
Cambia **las dos llamadas** a `describe(...)` por `analytics.describe(...)`.
El prefijo hace visible de dónde viene la función; sus argumentos no cambian.

### 5.b · Contrasta el resultado

Repite los dos comandos de 4.b. Deben conservarse tanto las salidas como el import
silencioso. Puedes conservar esta variante o volver a la versión inicial completa;
no mezcles una importación con llamadas de la otra forma.

## Criterio de cierre y continuidad

Puedes seguir una llamada desde `main.py` hasta `analytics.py` y `functional.py`,
explicar el caso `None` y distinguir importar de ejecutar. En L4 reutilizarás esta
organización: `main.py` importará una clase desde `models.py`. Una orden expresa una
intención; la nueva clase `Fill` representará una ejecución ya confirmada.
