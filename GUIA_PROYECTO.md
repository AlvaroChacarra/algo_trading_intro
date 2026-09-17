# Del notebook al programa

En todas las clases empezamos investigando en Jupyter. Cada celda permite probar una idea, inspeccionar un dato y explicar un resultado. El principal y los auxiliares incluyen salidas visibles y resultados esperados para contrastar tus respuestas.

## El mismo principal en Python

Después del notebook, abre `exercises/main.py`, guarda una copia como `mi_main.py` y traslada tus respuestas. Ejecuta desde la carpeta `exercises`:

```bash
python mi_main.py
```

El punto de entrada `main()` reúne los pasos del principal. Al ejecutar el archivo, Python recorre esos pasos seguidos. Esta segunda versión permite comprobar cómo pasa una investigación por celdas a un programa completo.

Una función reúne una operación que quieres reutilizar; un módulo `.py` puede agrupar funciones o clases; un paquete organiza varios módulos. Separar cálculos de su ejecución ayuda a reutilizar el código sin lanzar todo el experimento al hacer `import`. El curso introduce estas ideas progresivamente.

## Qué contiene la carpeta de ejercicios

| Archivo o carpeta | Para qué sirve |
|---|---|
| `NN_build_exercises.ipynb` | Principal de la clase, con tus respuestas en celdas. |
| `NN_auxiliary.ipynb` | Refuerzo, con su carácter obligatorio u opcional indicado. |
| `main.py` | Versión del principal ejecutable con Python. |
| `soluciones/` | Los mismos notebooks y script resueltos para comparar. |
| `exchange/`, cuando se proporciona | Biblioteca de referencia que usan los experimentos. |
| Datos y archivos de apoyo indicados en la clase | Entradas y herramientas ya preparadas para esos experimentos. |

Las piezas avanzan desde precios y objetos hasta libros, ejecuciones, backtests y estrategias. La biblioteca proporcionada permite experimentar con esas conexiones mientras completas la pieza de cada clase. El enunciado distingue el código preparado de lo que debes escribir tú.

## Proyecto final y repaso

L14 tiene además un capstone de 90 minutos: trabaja en `capstone.ipynb`, explica tus decisiones y prueba el programa equivalente `capstone.py`. Guarda tus copias como `mi_capstone.ipynb` y `mi_capstone.py`. Su solución es una referencia para comparar el procedimiento; un resultado en datos sintéticos no demuestra rentabilidad futura.

L15 utiliza notebooks y programa para el repaso histórico. El examen oficial acumulativo se administra por separado; sus preguntas y respuestas no forman parte de las soluciones de práctica.

Guarda las copias personales junto a las plantillas y actualiza desde la raíz con `git pull --ff-only`. La preparación completa está en [la guía local](GUIA_LOCAL.md).
