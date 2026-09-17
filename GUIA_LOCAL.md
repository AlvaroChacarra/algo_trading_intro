# Empieza aquí

**Presentaciones:** abre [la web del curso](https://alvarochacarra.github.io/algo_trading_intro/) y pulsa **Presentación** en tu clase. En tu ordenador también puedes abrir `index.html` con doble clic; funciona sin servidor.

## 1. Descarga e instala una vez

En [el repositorio público](https://github.com/AlvaroChacarra/algo_trading_intro), pulsa **Code → Download ZIP**. Extrae el ZIP y abre una terminal en la carpeta extraída. No necesitas Git ni cuenta de GitHub.

Instala **Python 3.11** y crea el entorno dentro de esa carpeta:

```bash
python -m venv .venv
```

Si tu ordenador usa `python3` o `py -3.11`, úsalo en ese comando.

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

En Jupyter usa **File → Save Notebook As…** para crear tu copia. Conserva las plantillas originales: reciben las mejoras del curso.

Resuelve el principal **en las celdas**, con **Shift+Enter**, de arriba abajo. Mira las salidas y compáralas con el resultado esperado. Los auxiliares son opcionales. Si cambias datos anteriores, vuelve a ejecutar desde ellos; al terminar, usa **Restart Kernel and Run All Cells**.

Para probar el mismo ejercicio como programa, copia `main.py` como `mi_main.py` y traslada tus respuestas. Abre una segunda terminal, activa el mismo entorno y entra en `exercises` de esa clase:

```bash
cd 01-python-i-data-model/exercises
python mi_main.py
```

El `.py` ejecuta el programa entero mediante `main()`. Ejecutar sin errores no garantiza un cálculo correcto: compara también los números. El notebook ya cubre el ejercicio; el script permite repetirlo como programa.

Desde las clases de objetos verás también `exercises/exchange/`: es una biblioteca proporcionada para los experimentos. Conserva esa carpeta junto a los notebooks; tus respuestas van en las celdas y en tu copia del script. Consulta las soluciones del principal y los auxiliares en `exercises/solutions/`, o ábrelas desde el README de la clase.

En L14, el proyecto final tiene además `capstone.ipynb` y `capstone.py`: crea `mi_capstone.ipynb` y `mi_capstone.py` en la misma carpeta. Reserva los 90 minutos indicados en su `CAPSTONE.md`.

## 3. Recibe material nuevo

Guarda tus notebooks. Descarga otra vez **Code → Download ZIP**, extrae en una carpeta temporal y copia las carpetas de las clases publicadas a tu carpeta del curso. Acepta actualizar las plantillas, conservando siempre tus archivos `mi_…`, que no vienen en el ZIP. No reemplaces ni borres tu carpeta completa ni su `.venv`. Conserva una copia de seguridad de tus respuestas antes de actualizar.

Si ya utilizas Git, puedes clonar el repositorio en lugar del ZIP y actualizar desde su raíz con `git pull --ff-only`. Los archivos personales `mi_…` están ignorados por Git. Si Git avisa de cambios en una plantilla, guarda primero tus respuestas con el nombre personal de la tabla y pide ayuda. No se requieren commits, ramas, push ni subir respuestas.

## Si ya tenías una copia del curso

Conserva tu carpeta anterior. El recorrido de todas las clases empieza ahora en sus notebooks. Si tenías módulos propios, consérvalos como trabajo personal y consulta los enunciados actuales para trasladar las respuestas.

[Del notebook al programa](GUIA_PROYECTO.md) explica cómo se conectan investigación, scripts y bibliotecas.
