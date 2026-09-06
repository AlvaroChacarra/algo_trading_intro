# Introducción al Algo Trading con Python — ICAI 2026

Construyes un proyecto acumulativo: representar el mercado, ejecutar órdenes, llevar cuentas y evaluar estrategias.

- [Presentaciones del curso](https://alvarochacarra.github.io/algo_trading_intro/)
- [Sesión 0: instalación y trabajo local](GUIA_LOCAL.md)
- [Descargar el material publicado](https://github.com/AlvaroChacarra/algo_trading_intro/archive/refs/heads/main.zip)

Python y los notebooks se ejecutan en tu ordenador. La guía prepara una carpeta propia y explica cómo añadir nuevas lecciones conservando tus respuestas.

Cada lección explica el problema, la teoría y las decisiones de diseño en la presentación. El cuaderno principal reúne toda la preparación LIVE/REQUIRED y la construcción de la siguiente pieza en tus archivos. El auxiliar contiene únicamente variantes y drills OPTIONAL del mismo problema. Los ejemplos proporcionados y tu implementación se identifican explícitamente.

## Cómo dar continuidad al estudio

Abre el **recorrido de estudio** del README o de los cuadernos de cada lección.
Recupera lo anterior, revisa la escena indicada, construye la pieza y consolida
en el cuaderno principal. Después elige un drill opcional según lo que te
cueste y vuelve al ejercicio indicado para comprobar que ya puedes explicarlo.
No necesitas completar todos los opcionales para seguir el curso.

El hilo es el mismo proyecto: dato → libro → ejecución → reloj → estrategia →
evaluación y control de inventario. Cada lección explica qué trasladar a tu
propio paquete y por qué lo necesitarás después.

En el cierre de cada presentación abre **Cómo construyes esta pieza en tu sistema**:
encontrarás el razonamiento y un ejemplo interpretable. El principal recupera esa
misma explicación y señala qué cuerpos completar en `student_project/exchange/`.
La lección termina al comprobar esos archivos con `python check_project.py N`.
El backtest sobre snapshots permite probar BuyOnce y señales; el experimento
de market making reutiliza la contabilidad en un simulador de llegadas separado.
Así conservamos las piezas sin atribuir ejecuciones pasivas a un replay que no las modela.

La sesión estándar dura aproximadamente 50 minutos: 10 de evaluación de contenido ya consolidado, 20 de presentación y 20 de práctica guiada. En sesiones consecutivas se difiere la evaluación hasta que haya tiempo de estudio. Evaluación: asistencia 10%, participación 20%, exámenes continuos 40%, final acumulativo 30%.

## Corrige tus ejercicios

Desde tu carpeta de estudio:

    python check_my_work.py 4
    python check_my_work.py 4 --aux
    python check_my_work.py all

Solo aparecen las lecciones que ya hayas descargado. Los datos de mercado del curso son sintéticos; los resultados son experimentos didácticos.

## Autoría

El repositorio público contiene material derivado y autorizado. La autoría, las soluciones docentes y el banco oficial se mantienen en el source privado. Las correcciones se publican desde allí.
