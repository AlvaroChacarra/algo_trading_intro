"""Small public notebook helpers. Validators are supplied by the lesson emitter."""
from __future__ import annotations

from contextlib import redirect_stdout
import inspect
import io
from pathlib import Path
import subprocess
import sys


class PracticeFeedback(AssertionError):
    """A real failure with a short Jupyter rendering instead of framework frames."""

    def _render_traceback_(self):
        return [str(self)]


def comprobar(exercise_id, namespace=None):
    """Check the current answer; keep technical checks outside the notebook."""
    if namespace is None:
        namespace = inspect.currentframe().f_back.f_globals
    try:
        with redirect_stdout(io.StringIO()):
            exec(compile(CHECKS[exercise_id], f'comprobación {exercise_id}', 'exec'), namespace)
    except Exception as exc:
        message = str(exc) or 'Revisa el resultado esperado de este paso.'
        feedback = message if message.startswith('⏸') else f'↻ {message}'
        raise PracticeFeedback(feedback) from None
    print('✓ Comprobado.')


def comprobar_proyecto(lesson):
    """Read saved learner files in a fresh process, never the reference package."""
    root = Path(__file__).resolve().parents[2]
    runner = root / 'check_project.py'
    if not runner.is_file():
        raise PracticeFeedback('Abre el cuaderno desde tu carpeta de estudio. Consulta GUIA_LOCAL.md.')
    result = subprocess.run([sys.executable, '-B', str(runner), str(lesson)],
                            cwd=root, capture_output=True, text=True, timeout=30)
    if result.returncode:
        problems = [line for line in result.stdout.splitlines()
                    if line.startswith('L') and 'integración OK' not in line]
        detail = '\n'.join(problems) or result.stderr.strip() or result.stdout.strip()
        raise PracticeFeedback('↻ Guarda tus archivos y revisa:\n' + detail)
    print(f'✓ Tu proyecto funciona hasta la clase {lesson}.')


# The emitter appends only public validation code, never private answers.
CHECKS = {}

CHECKS = {'L03-B04': "assert check_size(0.5) == 0.5\nassert make_safe_order(100, 0.5) == {'price': 100, 'size': 0.5}\nassert safe_order(100, 0.5) == {'price': 100, 'size': 0.5}\nfor invalid in (0, -0.5):\n    try:\n        check_size(invalid)\n    except ValueError as error:\n        assert str(invalid) in str(error), 'incluye el tamaño rechazado'\n    else:\n        raise AssertionError('check_size debe rechazar cero y negativos')\n    assert safe_order(100, invalid) is None\nfor invalid in (0, -5):\n    try:\n        make_safe_order(invalid, 1)\n    except ValueError as error:\n        assert str(invalid) in str(error), 'incluye el precio rechazado'\n    else:\n        raise AssertionError('rechaza el precio antes de crear la orden')\n    assert safe_order(invalid, 1) is None\ntry:\n    safe_order(None, 1)\nexcept TypeError:\n    pass\nelse:\n    raise AssertionError('safe_order solo debe capturar ValueError')\nprint('ok')\n", 'L03-A09': "assert types is not None, '⏸ types sigue en None: completa el ejercicio antes de validar'\nassert types == ['ok', 'falta un campo', 'tipo raro']\nassert classify_order({'size': 1}) == 'falta un campo'\nassert classify_order({'price': None, 'size': 1}) == 'tipo raro'\nassert classify_order({'price': 0, 'size': 0}) == 'ok'\nprint('ok')\n", 'L03-B08': "assert broken_output is not None, '⏸ broken_output sigue en None: completa el ejercicio antes de validar'\nassert import_output is not None, '⏸ import_output sigue en None: completa el ejercicio antes de validar'\nassert direct_output is not None, '⏸ direct_output sigue en None: completa el ejercicio antes de validar'\nassert broken_output == 'ARRANCANDO BACKTEST'\nassert import_output == '', 'la guardia omite la demo cuando el nombre es el del módulo'\nassert direct_output == 'ARRANCANDO BACKTEST'\nprint('ok')\n"}
