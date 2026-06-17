# Guion — Clase 6: OOP III — Herencia y polimorfismo

**Idea central:** Una clase base define el contrato; cada subclase decide a su manera. Llamar al mismo método sobre objetos distintos y que cada uno responda lo suyo: eso es polimorfismo.

Presentación de 3 bloques (~5-7 min cada uno) + hero + cierre.


## Bloque 1: Herencia: heredar y sobrescribir

- **Qué decir:** Una subclase hereda los métodos de su base y puede sobrescribir los que quiera. Compartes el esqueleto y cambias solo lo que difiere.
- **Acción en pantalla:** mostrar el snippet del bloque 1 y ejecutarlo en el notebook.

## Bloque 2: Clase abstracta (ABC): el contrato

- **Qué decir:** Una base abstracta con @abstractmethod no se puede instanciar: obliga a las subclases a implementar el método. Es la forma de fijar un contrato.
- **Acción en pantalla:** mostrar el snippet del bloque 2 y ejecutarlo en el notebook.

## Bloque 3: Polimorfismo: mismo método, respuestas distintas

- **Qué decir:** Recorres una lista de estrategias distintas y llamas a .decide() en todas; cada una responde lo suyo. El código que las usa no necesita saber cuál es cuál.
- **Acción en pantalla:** mostrar el snippet del bloque 3 y ejecutarlo en el notebook.

## Cierre
- Recoge la idea central y manda abrir `exercises/`.
