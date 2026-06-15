"""generate_exam.py — examen final del curso (Clase 15).

Formato: test de 40 min, 40 preguntas, 3 opciones (A/B/C).
Baremo: acierto +1, fallo -0.5, en blanco 0.
Cubre todo el curso: Python/OOP, framework exchange, microestructura, tipos de
orden y matching, ejecución VWAP, market making y Avellaneda-Stoikov.

Uso:  python generate_exam.py
Genera:  examen.html  y  examen_con_respuestas.html
"""

from __future__ import annotations

import html
import os

# (pregunta, opción A, B, C, correcta, tema)
QUESTIONS = [
    # --- Python / OOP / framework -----------------------------------------
    ("En el framework, ¿qué hace que una estrategia sea 'enchufable' al Backtest sin tocar el runner?",
     "Que herede de Strategy e implemente on_book_update devolviendo acciones",
     "Que defina un método run() propio",
     "Que importe el módulo backtest",
     "A", "framework"),
    ("`Side(str, Enum)` se usa en vez de un str pelado porque…",
     "Es más rápido en tiempo de ejecución",
     "Evita valores inválidos como 'byu' pero sigue comparándose con 'buy'",
     "Permite ordenar las órdenes por precio",
     "B", "oop"),
    ("Una `Order` de tipo MARKET tiene `price = None`. ¿Por qué?",
     "Porque el precio se decide al cruzar contra el libro, no se fija de antemano",
     "Porque las market orders no se ejecutan nunca",
     "Por un bug heredado del dict original",
     "A", "oop"),
    ("`PositionTracker` guarda `_cash` y `_position` con guión bajo. Esa convención significa…",
     "Que son constantes y no cambian",
     "Que son estado interno: se modifican vía métodos, no a mano desde fuera",
     "Que Python las hace inaccesibles (privadas de verdad)",
     "B", "oop"),
    ("¿Qué devuelve `on_book_update`?",
     "Una lista de acciones (NewOrder/Cancel), no ejecuta nada por sí misma",
     "Los fills generados",
     "El nuevo equity",
     "A", "framework"),
    ("En el Backtest de replay, una LIMIT que no se cruza en un snapshot…",
     "Persiste para siempre en el libro",
     "Solo descansa dentro de ese snapshot; el libro se reconstruye en el siguiente paso",
     "Se convierte automáticamente en MARKET",
     "B", "framework"),
    ("`Fill.cash_flow()` de una compra de 0.5 @ 100 vale…",
     "+50",
     "-50",
     "0",
     "B", "oop"),
    ("La composición que ve el alumno en L4 es…",
     "OrderBook contiene niveles; PositionTracker consume objetos Fill",
     "Order hereda de OrderBook",
     "Market hereda de Strategy",
     "A", "oop"),
    ("¿Por qué `on_book_update` devuelve acciones en vez de ejecutar órdenes directamente?",
     "Para separar la decisión (estrategia) de la ejecución (motor)",
     "Porque ejecutar dentro sería más rápido",
     "Para evitar usar clases",
     "A", "framework"),
    ("Polimorfismo en el curso significa que…",
     "VWAP y un market maker se enchufan al mismo Backtest sin cambiar el runner",
     "Una orden puede ser buy y sell a la vez",
     "El libro cambia de tipo en tiempo de ejecución",
     "A", "framework"),

    # --- Microestructura ---------------------------------------------------
    ("El spread es…",
     "best_ask - best_bid",
     "best_bid - best_ask",
     "(best_bid + best_ask)/2",
     "A", "microstructure"),
    ("El microprice pondera el mid por…",
     "El tamaño del lado contrario (más peso al lado con menos tamaño)",
     "El número de niveles del libro",
     "La volatilidad histórica",
     "A", "microstructure"),
    ("Un imbalance de nivel 1 cercano a +1 indica…",
     "Mucho más tamaño en el bid que en el ask (presión compradora)",
     "Mucho más tamaño en el ask",
     "Spread muy ancho",
     "A", "microstructure"),
    ("La profundidad (depth) de un lado mide…",
     "El tamaño acumulado en los primeros niveles",
     "La distancia al mid",
     "El número de trades ejecutados",
     "A", "microstructure"),
    ("El mid simple frente al microprice…",
     "El microprice suele anticipar mejor el siguiente movimiento a corto plazo",
     "Son siempre idénticos",
     "El mid es mejor predictor a corto",
     "A", "microstructure"),
    ("Liquidez visible en el libro vs negociación real:",
     "El libro muestra intención; no todo se ejecuta y puede cancelarse",
     "Todo lo del libro se ejecuta seguro",
     "Son lo mismo",
     "A", "microstructure"),

    # --- Tipos de orden y matching ----------------------------------------
    ("Una MARKET buy de tamaño grande sobre un libro fino…",
     "Barre varios niveles y paga un precio efectivo peor que el best ask",
     "Se ejecuta toda al best ask",
     "Se cancela si no hay liquidez al best ask",
     "A", "matching"),
    ("Una orden IOC…",
     "Cruza lo que pueda y cancela el remanente (no descansa)",
     "Se ejecuta entera o nada",
     "Descansa en el libro indefinidamente",
     "A", "matching"),
    ("Una orden FOK…",
     "O se llena entera o no se ejecuta nada",
     "Llena parcialmente y deja el resto",
     "Siempre cruza al mid",
     "A", "matching"),
    ("Una LIMIT buy al best_bid actual (por debajo del ask)…",
     "No cruza: descansa en el libro",
     "Cruza contra el ask inmediatamente",
     "Se rechaza",
     "A", "matching"),
    ("El precio efectivo de una market que barre niveles es…",
     "El nocional total dividido por el tamaño total ejecutado",
     "Siempre el best bid",
     "El precio del último nivel tocado",
     "A", "matching"),
    ("Más tamaño en una market order implica, normalmente…",
     "Peor precio efectivo (más slippage)",
     "Mejor precio efectivo",
     "El mismo precio efectivo",
     "A", "matching"),
    ("La elección del tipo de orden afecta a…",
     "Coste, probabilidad de ejecución y riesgo",
     "Solo a la latencia",
     "Solo al símbolo",
     "A", "matching"),
    ("Cruzar ya (market) vs esperar barato (limit) es un trade-off entre…",
     "Certeza de ejecución vs precio",
     "Volatilidad vs volumen",
     "Cash vs equity",
     "A", "matching"),

    # --- Ejecución / VWAP --------------------------------------------------
    ("El objetivo de un algoritmo VWAP es…",
     "Ejecutar cerca del precio medio ponderado por volumen, troceando la orden",
     "Maximizar el número de fills",
     "Comprar al best bid siempre",
     "A", "execution"),
    ("TWAP frente a VWAP:",
     "TWAP reparte en trozos iguales en el tiempo; VWAP pondera por volumen",
     "TWAP pondera por volumen; VWAP por tiempo",
     "Son idénticos",
     "A", "execution"),
    ("Trocear una orden grande sirve para…",
     "Reducir el impacto de mercado (slippage)",
     "Aumentar el slippage a propósito",
     "Evitar pagar comisiones",
     "A", "execution"),
    ("La predicción dinámica de volumen (L11) usa…",
     "El flujo reciente (ventana rolada) además de la media histórica",
     "Solo la media de todos los días",
     "Únicamente el primer minuto",
     "A", "execution"),
    ("El factor de corrección de un schedule…",
     "Acelera si vas por detrás del plan y frena si vas por delante",
     "Siempre manda el mismo tamaño",
     "Cancela la orden si hay retraso",
     "A", "execution"),
    ("El benchmark natural de una ejecución es…",
     "El mid de llegada (arrival mid)",
     "El precio de cierre del año",
     "El best ask final",
     "A", "execution"),
    ("Un equity positivo con un inventario enorme al final indica…",
     "Riesgo escondido: no es necesariamente una buena estrategia",
     "Una estrategia perfecta",
     "Un error de cálculo seguro",
     "A", "execution"),

    # --- Market making / Avellaneda-Stoikov -------------------------------
    ("El PnL de un market maker viene de…",
     "Comprar en el bid y vender en el ask, capturando el spread",
     "Cruzar market orders agresivas",
     "Pagar el spread cada vuelta",
     "A", "mm"),
    ("El principal riesgo de un market maker es…",
     "El inventario (posición acumulada cuando el flujo es desequilibrado)",
     "Tener demasiada caja",
     "Cotizar un spread demasiado ancho",
     "A", "mm"),
    ("El skew por inventario consiste en…",
     "Bajar ambas cotizaciones cuando estás largo para volver a plano",
     "Subir el spread sin mover el centro",
     "Cancelar todas las órdenes",
     "A", "mm"),
    ("El reservation price de Avellaneda-Stoikov con inventario largo…",
     "Está por debajo del mid (incentiva soltar)",
     "Está por encima del mid",
     "Coincide siempre con el mid",
     "A", "as"),
    ("En r = s - q·γ·σ²·(T-t), al acercarse el cierre (t→T)…",
     "El ajuste por inventario tiende a 0 y r vuelve al mid",
     "El ajuste se hace máximo",
     "r se vuelve infinito",
     "A", "as"),
    ("Subir γ (aversión al riesgo) en A-S…",
     "Inclina más el reservation price y reduce el inventario acumulado",
     "Aumenta el inventario acumulado",
     "No tiene ningún efecto",
     "A", "as"),
    ("La utilidad CARA -exp(-γ·W)…",
     "Es creciente en riqueza y más cóncava cuanto mayor es γ",
     "Es decreciente en riqueza",
     "Es lineal en riqueza",
     "A", "as"),
    ("Adverse selection para un market maker significa…",
     "Acumular posición justo cuando el mercado se mueve en tu contra",
     "Cotizar el mismo precio que el competidor",
     "Tener un spread negativo",
     "A", "mm"),
    ("¿Por qué el market making se simula con un modelo de intensidad de fills λ(δ)=A·e^(-κδ)?",
     "Porque una limit lejos del mid se ejecuta con menos probabilidad que una cerca",
     "Porque las market orders siempre fallan",
     "Porque el mid nunca se mueve",
     "A", "as"),
]


PAGE = """<!DOCTYPE html><html lang="es"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<style>
 body{{font-family:'Inter',system-ui,sans-serif;max-width:820px;margin:2rem auto;padding:0 1.2rem;color:#18181b;line-height:1.5}}
 h1{{font-size:1.6rem}} .meta{{background:#f4f4f5;border:1px solid #e4e4e7;border-radius:8px;padding:1rem 1.2rem;margin:1rem 0}}
 .q{{margin:1.1rem 0;padding:.8rem 1rem;border:1px solid #e4e4e7;border-radius:8px}}
 .qn{{font-weight:700}} .topic{{color:#71717a;font-size:.75rem;text-transform:uppercase;letter-spacing:.05em}}
 ol{{list-style:none;padding-left:0;margin:.5rem 0 0}} li{{margin:.25rem 0}}
 .opt{{font-weight:600;color:#0e7490;margin-right:.4rem}}
 .correct{{background:#dcfce7;border-color:#86efac}} .ans{{color:#15803d;font-weight:700}}
 @media print{{.q{{break-inside:avoid}}}}
</style></head><body>
<h1>{title}</h1>
<div class="meta">
 <b>Examen final — Introducción al Algo Trading con Python (ICAI 2026)</b><br>
 Duración: 40 minutos · 40 preguntas · 3 opciones (A/B/C).<br>
 <b>Baremo:</b> acierto <b>+1</b>, fallo <b>−0.5</b>, en blanco <b>0</b>.
</div>
{body}
</body></html>"""


def render(with_answers: bool) -> str:
    rows = []
    for i, (q, a, b, c, correct, topic) in enumerate(QUESTIONS, 1):
        opts = []
        for letter, text in zip("ABC", (a, b, c)):
            cls = "ans" if (with_answers and letter == correct) else ""
            mark = " ✔" if (with_answers and letter == correct) else ""
            opts.append(f'<li class="{cls}"><span class="opt">{letter}.</span>'
                        f'{html.escape(text)}{mark}</li>')
        qcls = "q correct" if with_answers else "q"
        rows.append(
            f'<div class="{qcls}"><div class="topic">{topic}</div>'
            f'<div class="qn">{i}. {html.escape(q)}</div>'
            f'<ol>{"".join(opts)}</ol></div>')
    title = ("Examen final — CLAVE DE RESPUESTAS" if with_answers
             else "Examen final")
    return PAGE.format(title=title, body="\n".join(rows))


def main() -> None:
    here = os.path.dirname(os.path.abspath(__file__))
    assert len(QUESTIONS) == 40, f"el examen debe tener 40 preguntas, tiene {len(QUESTIONS)}"
    with open(os.path.join(here, "examen.html"), "w") as f:
        f.write(render(False))
    with open(os.path.join(here, "examen_con_respuestas.html"), "w") as f:
        f.write(render(True))
    print(f"OK — {len(QUESTIONS)} preguntas. Generados examen.html y examen_con_respuestas.html")


if __name__ == "__main__":
    main()
