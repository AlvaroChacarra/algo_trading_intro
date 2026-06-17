# Clase 6 — OOP III — Herencia y polimorfismo (guía de implementación)

Pieza del framework: **una familia Strategy de juguete: base + subclases (semilla del framework de L10)**.

## Teoría que cubre

La pieza que sostiene todo el framework: vas a tener **muchas estrategias** que comparten un
esqueleto. La **herencia** deja que una subclase reutilice y **sobrescriba** los métodos de una
base. Una **clase abstracta** (`ABC` + `@abstractmethod`) fija un contrato: no se puede
instanciar hasta implementar el método. Y el **polimorfismo** es llamar al mismo método sobre
objetos distintos y que cada uno responda lo suyo — el código que los usa no necesita saber cuál
es cuál.

Se enseña construyendo una familia `Strategy` de juguete (Momentum, Contrarian): exactamente el
patrón que en la clase 10 se conecta al motor real. El alumno llega al framework con la herencia
ya dominada, no a presión.

## Implementación técnica

Pura OOP, sin dependencias: una base abstracta `Strategy` con `@abstractmethod decide` y
subclases que la implementan; un bucle polimórfico (`[s.decide(imb) for s in strategies]`).
Conceptos: herencia, override, `super().__init__`, `ABC`/`@abstractmethod`, `isinstance`,
polimorfismo. El `.py` entregable es `strategies_toy.py` (base + Momentum + Contrarian + bucle
polimórfico). Puente directo a L10: ese `Strategy` de juguete se formaliza como la interfaz del
framework y se enchufa al `Backtest`.

## Presentación (3 bloques)

1. **Herencia: heredar y sobrescribir** — Una subclase hereda los métodos de su base y puede sobrescribir los que quiera. Compartes el esqueleto y cambias solo lo que difiere.
2. **Clase abstracta (ABC): el contrato** — Una base abstracta con @abstractmethod no se puede instanciar: obliga a las subclases a implementar el método. Es la forma de fijar un contrato.
3. **Polimorfismo: mismo método, respuestas distintas** — Recorres una lista de estrategias distintas y llamas a .decide() en todas; cada una responde lo suyo. El código que las usa no necesita saber cuál es cuál.

## Cuaderno de construcción

Patrón por ejercicio: enunciado → starter (`pass`/`None`) → validador (`assert` con mensaje claro, tolerancia `1e-9`) → solución guiada embebida.
Tiers: **Núcleo** = los primeros (en clase), **Si vamos bien** = el resto, **Auxiliares** = cuaderno `06_auxiliary.ipynb`.

El contenido se genera desde `framework/_build/` — para editar esta clase, edita su spec y regenera con `build_course.py`. No edites a mano los notebooks.

## Continuidad

El paquete `exchange/` llega con lo construido hasta la clase anterior; hoy se añade la pieza nueva, que se convierte en el starter de la siguiente.
