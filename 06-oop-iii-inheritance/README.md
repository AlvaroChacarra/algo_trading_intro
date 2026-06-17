# Clase 6 — OOP III — Herencia y polimorfismo

> La pieza que sostendrá todo el framework: muchas estrategias que comparten un esqueleto. Aprendes herencia, sobrescritura, clases abstractas y polimorfismo construyendo tus primeras estrategias de juguete.

## Contexto teórico

La pieza que sostiene todo el framework: vas a tener **muchas estrategias** que comparten un
esqueleto. La **herencia** deja que una subclase reutilice y **sobrescriba** los métodos de una
base. Una **clase abstracta** (`ABC` + `@abstractmethod`) fija un contrato: no se puede
instanciar hasta implementar el método. Y el **polimorfismo** es llamar al mismo método sobre
objetos distintos y que cada uno responda lo suyo — el código que los usa no necesita saber cuál
es cuál.

Se enseña construyendo una familia `Strategy` de juguete (Momentum, Contrarian): exactamente el
patrón que en la clase 10 se conecta al motor real. El alumno llega al framework con la herencia
ya dominada, no a presión.

## Qué construyes hoy

**una familia Strategy de juguete: base + subclases (semilla del framework de L10)**

Pura OOP, sin dependencias: una base abstracta `Strategy` con `@abstractmethod decide` y
subclases que la implementan; un bucle polimórfico (`[s.decide(imb) for s in strategies]`).
Conceptos: herencia, override, `super().__init__`, `ABC`/`@abstractmethod`, `isinstance`,
polimorfismo. El `.py` entregable es `strategies_toy.py` (base + Momentum + Contrarian + bucle
polimórfico). Puente directo a L10: ese `Strategy` de juguete se formaliza como la interfaz del
framework y se enchufa al `Backtest`.

## Ejercicios de construcción

- **1. Una clase base con un método** — clase base
- **2. Hereda y sobrescribe** — herencia + override
- **3. El contrato: clase abstracta** — ABC + @abstractmethod
- **4. Polimorfismo** — mismo método, objetos distintos
- **5. super() en el __init__** — reutilizar la base
- **6. Tu familia de estrategias** — juntar herencia + polimorfismo

## Estructura de la carpeta

- `presentation/` — presentación interactiva + guion del profesor
- `exercises/06_build_exercises.ipynb` — construyes la pieza (núcleo 1-3, luego el resto)
- `exercises/06_auxiliary.ipynb` — profundización opcional
- `exercises/exchange/` — el paquete que vienes construyendo (starter de hoy)

## Idea central

> Una clase base define el contrato; cada subclase decide a su manera. Llamar al mismo método sobre objetos distintos y que cada uno responda lo suyo: eso es polimorfismo.
