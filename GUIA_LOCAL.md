# Empieza aquí

**Presentaciones:** abre [la web del curso](https://alvarochacarra.github.io/algo_trading_intro/) y pulsa **Presentación** en tu clase. En tu ordenador también puedes abrir `index.html` con doble clic; funciona sin servidor.

## 1. Descarga el curso una vez

Instala **Python 3.11** y **Git**. Abre una terminal:

```bash
git clone https://github.com/AlvaroChacarra/algo_trading_intro.git
cd algo_trading_intro
python -m venv .venv
```

Si tu ordenador usa `python3` o `py -3.11`, úsalo en el último comando. El repositorio público no requiere cuenta de GitHub.

Activa Python dentro de esta carpeta:

| Terminal | Comando |
|---|---|
| Windows PowerShell | `.\.venv\Scripts\Activate.ps1` |
| macOS / Linux | `source .venv/bin/activate` |

```bash
python -m pip install -r requirements.txt
python -m ipykernel install --sys-prefix --name algo-trading --display-name "Algo Trading"
python -m notebook
```

Si PowerShell bloquea la activación, usa `.\.venv\Scripts\python.exe` en lugar de `python` en estos tres comandos; no cambies las políticas del sistema. Jupyter se abrirá en el navegador. Selecciona el kernel **Algo Trading**.

## 2. Trabaja en la clase

Abre la carpeta de tu clase y después `exercises`. El número del archivo cambia con la clase:

| Plantilla | Tu copia en la misma carpeta |
|---|---|
| `01_build_exercises.ipynb` | `mi_principal.ipynb` |
| `01_auxiliary.ipynb` | `mi_auxiliar.ipynb` |
| `main.py` | `mi_main.py` |

En Jupyter usa **File → Save Notebook As…** para crear tu copia. Conserva las plantillas originales: reciben las mejoras del curso. Tus archivos `mi_…` están ignorados por Git y se quedan en tu ordenador.

Resuelve el principal y los auxiliares **en las celdas**, con **Shift+Enter**, de arriba abajo. Mira las salidas y compáralas con el resultado esperado. Sigue las etiquetas de trabajo obligatorio u opcional de cada notebook. Si cambias datos anteriores, vuelve a ejecutar desde ellos; al terminar, usa **Restart Kernel and Run All Cells**.

El notebook sirve para investigar: experimentar por partes, mirar datos y explicar resultados. Para probar el mismo ejercicio como programa, copia `main.py` como `mi_main.py` y traslada tus respuestas. Abre una segunda terminal, activa el mismo entorno y entra en `exercises` de esa clase:

```bash
cd 01-python-i-data-model/exercises
python mi_main.py
```

El `.py` ejecuta el programa entero mediante `main()`; las funciones permiten organizar código reutilizable. Ejecutar sin errores no garantiza un cálculo correcto: compara también los números. La versión `.py` es otra forma de ejecutar el principal; el notebook ya cubre el ejercicio.

Desde las clases de objetos verás también `exercises/exchange/`: es una biblioteca de referencia proporcionada para los experimentos. Las celdas indican qué funciones usan. Conserva esa carpeta junto a los notebooks; tus respuestas van en las celdas y en tu copia del script.

**Para contrastar tu respuesta:** `exercises/soluciones/` contiene los notebooks principal y auxiliar resueltos y un `main.py` resuelto. Puedes ejecutar sus celdas directamente; desde esa carpeta, `python main.py` ejecuta la solución del principal. Las plantillas de práctica siguen en `exercises/`.

En L14, el proyecto final tiene además `capstone.ipynb` y `capstone.py`: crea `mi_capstone.ipynb` y `mi_capstone.py` en la misma carpeta. Sus soluciones están también en `soluciones/`. Reserva los 90 minutos indicados en `CAPSTONE.md`.

## 3. Recibe material nuevo

Guarda tus notebooks. Desde la carpeta `algo_trading_intro`, ejecuta:

```bash
git pull --ff-only
```

Luego vuelve a abrir el curso. Aparecerán las clases publicadas y las plantillas corregidas. Tus copias personales permanecen intactas; compara una plantilla corregida con tu copia para incorporar la mejora. No necesitas commits, ramas, push ni subir respuestas.

Si Git avisa de cambios en una plantilla, **no los descartes**: guarda primero tus respuestas con el nombre personal de la tabla y pide ayuda para restaurar la plantilla.

Las copias personales no se suben a GitHub: conserva una copia de seguridad como harías con cualquier trabajo local.

## Si ya tenías una copia del curso

Conserva tu carpeta anterior. Clona el repositorio y copia tus respuestas con los nombres personales anteriores. El recorrido de todas las clases empieza ahora en sus notebooks. Si tenías módulos propios de la versión anterior, consérvalos como trabajo personal y consulta los enunciados actuales para trasladar las respuestas.

[Del notebook al programa](GUIA_PROYECTO.md) explica cómo se conectan investigación, scripts y bibliotecas.
