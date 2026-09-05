# Sesión 0 — trabajar en tu ordenador

Descarga el ZIP de [material publicado](https://github.com/AlvaroChacarra/algo_trading_intro/archive/refs/heads/main.zip) y descomprímelo. Necesitas Python 3.11. La web contiene las presentaciones; los ejercicios se resuelven aquí.

## 1. Prepara tu carpeta de estudio

Abre una terminal dentro de la carpeta descomprimida:

    python course_workspace.py ../mi-curso
    cd ../mi-curso
    python -m venv .venv

Si tu instalación de macOS llama al intérprete python3, usa python3 en esos comandos. En Windows puedes usar py -3.11 si python no está disponible.

Activa el entorno:

- Windows PowerShell: .venv\Scripts\Activate.ps1
- macOS: source .venv/bin/activate

En PowerShell también puedes usar directamente .venv\Scripts\python.exe para los comandos siguientes sin activar el entorno ni cambiar políticas del sistema.

    python -m pip install -r requirements.txt
    python -m ipykernel install --user --name algo-trading --display-name "Algo Trading"
    python -m notebook

## 2. Comprueba el kernel

Abre 01-python-i-data-model/exercises/01_build_exercises.ipynb y selecciona el kernel Algo Trading. Ejecuta una celda nueva:

    import sys
    print(sys.executable)
    print(2 + 3)

La ruta debe apuntar al Python de mi-curso/.venv y el resultado debe ser 5. Si no coincide, selecciona el kernel registrado desde ese entorno antes de continuar.

Resuelve una respuesta y ejecuta su comprobación. Las respuestas sin completar aparecen como pendientes en el comprobador de terminal:

    python check_my_work.py 1

Desde L3 importarás tu módulo. Reinicia el kernel después de editar un archivo .py para no usar una versión antigua guardada en memoria. Cada cuaderno indica dónde se conserva su implementación.

## 3. Recibe la siguiente lección

Descarga el ZIP actualizado, descomprímelo en una carpeta de materiales nueva y ejecuta desde ella:

    python course_workspace.py ../mi-curso

Usa la ruta real a la misma carpeta de estudio. Se añaden los archivos nuevos y se conservan todos los existentes: una actualización no reemplaza tus respuestas. Si una lección anterior recibe una corrección, compárala con la nueva descarga y traslada el cambio necesario; no sustituyas su carpeta completa.

Los notebooks y datos de lecciones futuras aparecen cuando se publiquen. No necesitas acceso al repositorio privado, GitHub Classroom ni subir tus respuestas a GitHub.

## Tu proyecto continúa entre clases

La carpeta `student_project/exchange/` contiene tus archivos Python. Completa los
huecos que indique el cierre de cada notebook y ejecuta desde la raíz de tu copia:

```bash
python check_project.py 1
```

Sustituye `1` por la clase alcanzada. El comando comprueba también las anteriores
y muestra qué carpeta importa. `check_my_work.py` comprueba los miniejercicios del
notebook; `check_project.py` comprueba la integración de tus archivos reales.

Cada actualización añade módulos nuevos sin sobrescribir los existentes. Los
archivos de `exercises/exchange/` son referencias para experimentar; el proyecto
acumulativo tiene una API reducida y documentada en sus propios archivos. Trabaja
siempre en tu copia de estudio, no dentro de la descarga que sustituirás después.
