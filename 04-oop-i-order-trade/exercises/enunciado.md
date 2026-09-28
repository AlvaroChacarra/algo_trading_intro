# Lesson 4 · Tu primera clase utilizada desde otro archivo

## Objetivo

Construir `Fill`, una clase que reúne los datos y el comportamiento de una
**ejecución confirmada**. Una orden expresa una intención de comprar o vender;
un fill representa lo que ya se ejecutó. En L3 importabas funciones; ahora
`main.py` importará una clase y creará dos objetos a partir de ella.

## Archivos

| Archivo | Tu trabajo |
| --- | --- |
| `models.py` | Completar atributos, `cash_flow()` y `__repr__()` de `Fill`. |
| `main.py` | Importar la clase y utilizarla en los ejercicios. |
| `solutions/solucion.md` | Referencia textual por archivo y ejercicio. |

## Cómo trabajar

Abre los archivos juntos en `exercises`. Sigue la numeración: cada apartado
coincide con un `TODO · Ejercicio N.a` donde debes actuar. Sustituye los `pass`
de los métodos por tu código y guarda **ambos archivos** antes de ejecutar
`python main.py` desde esa carpeta. Al principio están incompletos; comprueba
cada paso a medida que lo terminas. No copies la clase dentro de `main.py`.
Si guardas una copia personal, conserva juntos ambos archivos y sus imports.
La validación y la guarda final están proporcionadas; no necesitas reescribirlas.

Ejercicios 1–4: núcleo presencial (unos 20 min). Ejercicios 5–6: consolidación
requerida (unos 8 min de estudio). Ejercicio 7: OPTIONAL (unos 3 min).
Consulta la solución después de intentar cada parte.

## Ejercicio 1 · Prepara la clase y su importación

### 1.a · Conserva los datos en `models.py`

En `__init__`, después de la validación, asigna `side`, `price` y `size` a
`self.side`, `self.price` y `self.size`. `__init__` prepara cada objeto nuevo;
`self` se refiere a ese objeto. Los parámetros recibidos deben quedar guardados
como atributos para que otros métodos puedan consultarlos después.

La validación de lado y números positivos finitos ya está escrita: déjala intacta.
No necesitas estudiar `isfinite` para completar la tarea. Una entrada inválida
produce `ValueError` antes de guardar los datos.

### 1.b · Importa en `main.py`

Fuera de `main()`, escribe `from models import Fill`. Igual que en L3, importas
una pieza de otro archivo: la clase debe tener una sola definición.

## Ejercicio 2 · Crea dos instancias independientes

### 2.a · Construye los objetos en `main.py`

Dentro de `main()`, crea `buy = Fill('buy', 100, 2)` y
`sell = Fill('sell', 110, 2)`. El orden de argumentos es lado, precio por unidad
y número de unidades. Cada llamada crea una instancia distinta de la misma clase.

### 2.b · Comprueba sus atributos

Imprime `side`, `price` y `size` de `buy`, luego de `sell`, y otra vez de `buy`.
Usa las etiquetas `Compra:`, `Venta:` y `Compra intacta:`. Antes de ejecutar,
pregúntate: ¿crear la venta modifica la compra?

<details>
<summary>Comprobar después de predecir y ejecutar</summary>

Esperas:

```text
Compra: buy 100 2
Venta: sell 110 2
Compra intacta: buy 100 2
```

Cada instancia conserva sus datos: `self` no es un almacén compartido entre ellas.

</details>

## Ejercicio 3 · Consulta el comportamiento

### 3.a · Completa `cash_flow()` en `models.py`

Devuelve precio por tamaño usando los atributos de la instancia. El signo es
negativo para `buy` (pagamos) y positivo para `sell` (cobramos). Puedes decidir
el signo con un `if` y después multiplicar. Usa `return`, no `print`: el programa
necesita el número para calcular con él. No cambies atributos ni acumules caja aquí.

### 3.b · Llama al método desde `main.py`

Imprime, con etiqueta `Flujos:`, `buy.cash_flow()`, `sell.cash_flow()` y una segunda
consulta a `buy.cash_flow()`. Predice antes el resultado: `-200 220 -200`.
Los paréntesis ejecutan el método y Python vincula `self` con el objeto situado
antes del punto. Repetir la consulta no registra una nueva ejecución ni paga otra vez.

## Ejercicio 4 · Cierra una posición completa

### 4.a · Calcula caja y unidades en `main.py`

Supón que partes sin posición ni caja invertida y que no hay comisiones. Guarda en
`total_cash` la suma de `buy.cash_flow()` y `sell.cash_flow()`. Guarda en
`remaining_units` la diferencia `buy.size - sell.size`. Usa los resultados de los
objetos, no escribas directamente los números esperados.

### 4.b · Interpreta el cierre

Imprime ambos valores con etiquetas `Caja neta:` y `Unidades restantes:`.
Esperas **20 y 0**: pagaste 200, cobraste 220 y no queda ninguna unidad.
En este escenario cerrado y sin comisiones, la caja neta coincide con el beneficio.
La clase representa cada ejecución; es `main.py` quien combina sus resultados.

## Ejercicio 5 · Consolida con una venta parcial

### 5.a · Cambia el escenario en `main.py`

Crea `partial_sell = Fill('sell', 110, 1)`. Es un escenario alternativo:
la misma compra inicial y una venta de **una** unidad en lugar de dos.
No sumes también la venta completa `sell`: estarías mezclando dos escenarios.

### 5.b · Separa dinero de posición

Calcula `partial_cash` sumando los flujos de `buy` y `partial_sell`, y recalcula
`remaining_units` con sus tamaños. Imprime los dos valores precedidos de
`Venta parcial: caja / unidades:`. Esperas **−90 y 1**: pagaste 200 y cobraste 110,
pero todavía tienes una unidad. Escribe o explica por qué −90 no es por sí solo
la pérdida total: falta valorar la unidad que conservas.

## Ejercicio 6 · Haz legible el objeto y observa un error

### 6.a · Completa `__repr__()` en `models.py`

Sustituye la cadena provisional por una construida con los atributos de `self`.
Para la compra del ejemplo debe devolver `Fill(buy 2 @ 100)`; para otros datos,
debe reflejar esos datos. Una f-string permite insertar los atributos entre llaves.
Devuelve la cadena sin imprimirla dentro del método.

### 6.b · Utiliza representación y validación en `main.py`

Primero imprime `buy`: Python utilizará la representación que acabas de definir.
Después intenta crear `Fill('buy', -10, 2)` dentro de `try`. Captura únicamente
`ValueError as error` e imprime `Ejecución rechazada:` junto con `error`, igual que
trataste la orden inválida en L3. Esperas el mensaje proporcionado:
`fill requiere lado válido y valores positivos finitos`. No desactives la validación.

### 6.c · Comprueba ejecución e importación

Conserva la guarda `if __name__ == '__main__':` del final. Ejecuta en terminal,
desde `exercises`, por separado:

```bash
python main.py
python -c "import main"
```

El primero muestra los resultados anteriores y el rechazo controlado; el segundo
no imprime nada. Importar permite reutilizar definiciones sin ejecutar la demostración.

## Ejercicio 7 · OPTIONAL · Dos experimentos con atributos

Añade cada experimento al final de `main()`, con su sangría, después del `try/except`.
No son necesarios para continuar a L5.

### 7.a · Modifica una sola instancia

Crea `f` y `g`, ambas `Fill('buy', 100, 2)`. Cambia solo `f.price` a 110 e imprime
los flujos de las dos. Esperas **−220 y −200**: el método consulta los atributos
actuales del objeto que recibe la llamada; cambiar `f` no modifica `g`.

### 7.b · Distingue guardar de recalcular

Vuelve a crear `f = Fill('buy', 100, 2)` para comenzar con precio 100. Asigna
`f.notional = f.price * f.size`; aquí notional es el importe sin signo. Cambia
`f.price` a 110 e imprime `f.notional` y `f.price * f.size`. Esperas **200 y 220**:
la asignación guardó un número, no una fórmula que se actualice sola.

## Criterio de cierre y continuidad

Puedes seguir `main.py → Fill → atributos → valor devuelto`, explicar el signo de
cada flujo y distinguir caja de posición. En L5, `PositionTracker` reutilizará `Fill`
para mantener caja y unidades al registrar ejecuciones. Esta clase todavía no es
una cuenta: consultar `cash_flow()` solo devuelve un número.
