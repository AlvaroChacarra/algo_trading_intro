# Del notebook al paquete — desde L4

En L1–L3 ya has construido `spread`, `mid`, `best_prices` y `describe`. Desde L4 las clases añaden objetos y los reúnen en un paquete llamado `exchange`.

## Preparación al comenzar L4

Trabaja dentro del mismo repositorio que actualizas con `git pull`:

1. Crea las carpetas `student_project/exchange` y un archivo vacío `__init__.py` dentro de `exchange`. Este archivo indica que la carpeta es un paquete Python.
2. Copia ahí los `.py` de `04-oop-i-order-trade/exercises/project_starter`. Incluyen las plantillas de las piezas anteriores y la nueva de L4.
3. Traslada tus respuestas de los notebooks: `spread` y `mid` a `snapshot.py`, `best_prices` a `functional.py` y `describe` a `application.py`. Conserva el import que ya trae `application.py`: ahora reutiliza tu función de `functional.py`.
4. Continúa con el principal de L4 y completa `models.py`.

El código proporcionado alrededor de los huecos conecta las piezas. No reemplaces tus respuestas por el paquete de referencia de `exercises/exchange`.

`student_project/` está ignorado por Git: tus cambios permanecen al actualizar. Si ya tenías ese paquete en la versión anterior, cópialo completo y conserva tus archivos.

## Clases siguientes

Después de actualizar, copia únicamente los archivos nuevos de `exercises/project_starter` a tu paquete. No sobrescribas los que ya completaste. El principal de cada clase indica la siguiente pieza y su comprobación acumulativa; los validadores de L4–L14 conservan su funcionamiento anterior.

Desde la raíz del repositorio, por ejemplo en L4:

```bash
python check_project.py 4
```

La comprobación importa tus archivos reales e incluye las piezas anteriores. La carpeta permanece en el mismo repositorio; no necesitas generar otra copia del curso.
