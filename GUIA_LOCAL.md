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

Abre la carpeta de tu clase y después `exercises`:

| Plantilla | Tu copia en la misma carpeta |
|---|---|
| `01_build_exercises.ipynb` (el número cambia por clase) | `mi_principal.ipynb` |
| `01_auxiliary.ipynb` | `mi_auxiliar.ipynb` |
| `main.py` | `mi_main.py` |

En Jupyter usa **File → Save Notebook As…** para crear tu copia. Conserva las plantillas originales: reciben las mejoras del curso. Tus archivos `mi_…` están ignorados por Git y se quedan en tu ordenador.

En L1–L3 resuelve el principal y el auxiliar **en las celdas**, con **Shift+Enter**, de arriba abajo. Mira las salidas y compáralas con el resultado esperado. Si cambias datos anteriores, vuelve a ejecutar desde ellos; al terminar, usa **Restart Kernel and Run All Cells**.

El notebook sirve para investigar: experimentar por partes, mirar datos y explicar resultados. Para probar el mismo ejercicio como programa, copia `main.py` como `mi_main.py` y traslada tus respuestas. Abre una segunda terminal, activa el mismo entorno y entra en `exercises` de esa clase:

```bash
cd 01-python-i-data-model/exercises
python mi_main.py
```

El `.py` ejecuta el programa entero; sus funciones también pueden reutilizarse mediante `import`, que veremos en L3. Ejecutar sin errores no garantiza un cálculo correcto: compara también los números. La versión `.py` es una segunda forma de ejecutar el principal; el notebook ya cubre el ejercicio.

## 3. Recibe material nuevo

Guarda tus notebooks. Desde la carpeta `algo_trading_intro`, ejecuta:

```bash
git pull --ff-only
```

Luego vuelve a abrir el curso. Aparecerán las clases publicadas y las plantillas corregidas. Tus copias personales permanecen intactas; compara una plantilla corregida con tu copia para incorporar la mejora. No necesitas commits, ramas, push ni subir respuestas.

Si Git avisa de cambios en una plantilla, **no los descartes**: guarda primero tus respuestas con el nombre personal de la tabla y pide ayuda para restaurar la plantilla.

Las copias personales no se suben a GitHub: conserva una copia de seguridad como harías con cualquier trabajo local.

## Si ya tenías una copia del curso

Conserva tu carpeta anterior. Clona el repositorio y copia tus respuestas L1–L3 con los nombres personales anteriores. No necesitas ejecutar el antiguo creador de carpetas ni sus comprobadores.

La organización acumulativa de L4–L14 continúa en [la guía del proyecto](GUIA_PROYECTO.md), cuando empezamos a organizar paquetes y objetos.
