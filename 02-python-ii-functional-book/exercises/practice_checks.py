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

CHECKS = {'L02-B03': "assert new_list is not None, '⏸ new_list sigue en None: completa el ejercicio antes de validar'\nassert same_order is not None, '⏸ same_order sigue en None: completa el ejercicio antes de validar'\nassert new_list == [{'id': 2, 'size': 0.2}]\nassert new_list is not book and same_order is True\nassert book == [{'id': 1, 'size': 0.5}, {'id': 2, 'size': 0.2}]\nfor cancel in (cancel_order, cancel_compact):\n    original = [{'id': 2}, {'id': 1}, {'id': 3}]\n    result = cancel(original, 1)\n    assert result == [{'id': 2}, {'id': 3}], 'conserva el orden de llegada'\n    assert result is not original and len(original) == 3\n    assert result[0] is original[0] and result[1] is original[2]\n    absent = cancel(original, 99)\n    assert absent == original and absent is not original\n    assert cancel([], 1) == []\nprint('ok')\n", 'L02-B06': "assert imbalance(book) == 0.5\nassert imbalance([]) is None\nassert imbalance([{'side': 'buy', 'size': 0}]) is None\nassert imbalance([{'side': 'buy', 'size': 4}]) == 1\nassert imbalance([{'side': 'sell', 'size': 4}]) == -1\nassert imbalance([{'side': 'buy', 'size': 2}, {'side': 'sell', 'size': 2}]) == 0\nassert len(book) == 3\nprint('ok')\n", 'L02-B10': "assert ordered is not None, '⏸ ordered sigue en None: completa el ejercicio antes de validar'\nassert ordered_lambda is not None, '⏸ ordered_lambda sigue en None: completa el ejercicio antes de validar'\nassert get_price({'price': 7}) == 7\nassert [order['id'] for order in ordered] == ['B', 'A', 'C']\nassert ordered_lambda == ordered\nassert ordered is not orders and ordered_lambda is not orders\nassert [order['id'] for order in orders] == ['A', 'B', 'C']\nassert ordered[0] is orders[1]\nprint('ok')\n", 'L02-A05': "assert fee(100000) == 10\nassert fee(100000, 5) == 50\nassert fee(20000, bps=0) == 0, 'el argumento explícito sustituye el default'\nassert fee(0) == 0\nprint('ok')\n"}
